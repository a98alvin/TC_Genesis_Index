"""
Calculates common metrics from the confusion matrix/
contingency table.

References
----------
[1] Wilks, 2019: Statistical Methods in the Atmospheric Sciences.
"""

import numpy as np
from sklearn.metrics import confusion_matrix

__author__ = 'Christopher Slocum'
__copyright__ = 'Copyright 2019'
__version__ = '1.0c'
__maintainer__ = 'Christopher Slocum'


class ConfusionMatrix:

    def __init__(self, y_true, y_pred):
        """
        Binary truth values and predictions

        Parameters
        ----------
        y_true : array-like
            the truth
        y_pred : array-like
            the predicted values from a model
        """
        tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
        self.true_negative = tn
        self.false_positive = fp
        self.false_negative = fn
        self.true_positive = tp
        self.total = tn + fp + fn + tp
        self._prob_detection = None

    def false_alarm_ratio(self):
        """
        False alarm ratio

        the fraction of "yes" forecasts that turn out to be wrong, or that
        proportion of the forecast events that fail to materialize.
        """
        return self.false_positive / (self.true_positive + self.false_positive)

    def hit_pod(self):
        """
        hit rate or probability of detection

        the ratio of correct forecasts to the number of times the event of
        interest occurred.
        """
        if self._prob_detection is None:
            self._prob_detection = self.true_positive / (self.true_positive + self.false_negative)
        return self._prob_detection

    def false_alarm_rate_pofd(self):
        """
        false alarm rate or probability of false detection

        ratio of false alarms to the total number of nonoccurrences of the event
        """
        return self.false_positive / (self.false_positive + self.true_negative)

    def threat_score_csi(self):
        """
        Threat score or critical success index

        is the number of correct "yes" forecasts divided by the total number
        of occasions on which that event was forecast and/or observed.
        """
        return self.true_positive / (self.true_positive + self.false_positive + self.false_negative)

    def bias_ratio(self):
        """
        Bias ratio

        comparison of the average forecast with the average observation

        Bias greater than one indicates that the event was forecast more often
        than observed, which is called overforecasting. Less than one
        is called underforecasting.
        """
        return (self.true_positive + self.false_positive) / (self.true_positive + self.false_negative)

    def accuracy_proportion_correct(self):
        """
        Accuracy or proportion correct

        the fraction of the forecast occasions for which the nonprobabilistic
        forecast correctly anticipated the subsequent event or nonevent.
        """
        return (self.true_positive + self.true_negative) / self.total

    def odds_ratio(self):
        """
        Odds ratio

        the ratio of the conditional odds of a hit, given that the event occurs,
        to the conditional odds of a false alarm.
        """
        return (self.true_positive * self.true_negative) / (self.false_positive * self.false_negative)

    def extremal_dependence_index(self):
        """
        Extremal Dependence Index (see Ferro and Stephenson 2011)

        This measure takes on values between +/- 1, with positive values
        indicating better performance than random forecasts.
        """
        return (np.log(self.false_alarm()) - np.log(self.prob_detection())) / (np.log(self.false_alarm()) + np.log(self.prob_detection()))

    def heidke_ss(self):
        """
        Heidke Skill Score

        perfect forecasts receive HSS = 1, forecasts equivalent to the
        reference forecasts receive zero scores, and forecasts worse than
        the reference forecasts receive negative scores.
        """
        hss = 2 * (self.true_positive * self.true_negative - self.false_positive * self.false_negative)
        hss /= (self.true_positive + self.false_negative) * (self.false_negative + self.true_negative) + (self.true_positive + self.false_positive) * (self.false_positive + self.true_negative)
        return hss

    def peirce_ss(self):
        """
        Peirce Skill Score

        the difference between two conditional probabilities in the
        likelihood-base rate factorization of the joint distribution:
        the hit rate and the false alarm rate
        """
        pss = self.true_positive * self.true_negative - self.false_positive * self.false_negative
        pss /= (self.true_positive + self.false_negative) * (self.false_negative + self.true_negative)
        return pss

    def odds_ss(self):
        """
        Odds Ratio Skill Score
        """
        odds = (self.true_positive * self.true_negative) - (self.false_positive * self.false_negative)
        odds /= (self.true_positive * self.true_negative) + (self.false_positive * self.false_negative)
        return odds

    def css(self):
        """
        Clayton Skill Score

        the difference of the conditional probabilities
        """
        css = (self.true_positive * self.true_negative) - (self.false_positive * self.false_negative)
        css /= (self.true_positive + self.false_positive) * (self.false_negative + self.true_negative)
        return css

    def gss(self):
        """
        Gilbert Skill Score

        """
        aref = ((self.true_positive + self.false_positive) * (self.true_positive + self.false_negative)) / self.total
        gss = self.true_positive - aref
        gss /= self.true_positive - aref + self.false_positive + self.false_negative
        return gss
