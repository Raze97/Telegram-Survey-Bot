"""
Copyright: (c) 2020, Michael Barthelmäs, Marcel Killinger, Johannes Keller
GNU General Public License v3.0 (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

This file is part of Telegram Survey Bot.

Telegram Survey Bot is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Telegram Survey Bot is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Telegram Survey Bot.  If not, see <http://www.gnu.org/licenses/>.
"""
from datetime import datetime, time
from typing import List

from bot_utils.bot_enums import EndUrlDistribution


class DayCalculationSettings(object):
    daily_SurveyDays: List[int]
    end_SurveyDays: List[int]

    def __init__(self,
                 daily_SurveyDays: List[int],
                 end_SurveyDays: List[int],
                 *args, **kwargs):
        self.daily_SurveyDays: List[int] = daily_SurveyDays
        self.end_SurveyDays: List[int] = end_SurveyDays


class TimeCalculationSettings(object):
    daily_DelayMinutesAfterWakeup: int
    daily_SurveysPerDay: int
    daily_DelayMinutesBetweenSurveys: int
    end_DelayMinutesAfterWakeup: int
    end_SurveysPerDay: int
    end_DelayMinutesBetweenSurveys: int

    def __init__(self,
                 daily_DelayMinutesAfterWakeup: int,
                 daily_SurveysPerDay: int,
                 daily_DelayMinutesBetweenSurveys: int,
                 end_DelayMinutesAfterWakeup: int,
                 end_SurveysPerDay: int,
                 end_DelayMinutesBetweenSurveys: int,
                 *args, **kwargs):
        self.daily_DelayMinutesAfterWakeup: int = daily_DelayMinutesAfterWakeup
        self.daily_SurveysPerDay: int = daily_SurveysPerDay
        self.daily_DelayMinutesBetweenSurveys: int = daily_DelayMinutesBetweenSurveys
        self.end_DelayMinutesAfterWakeup: int = end_DelayMinutesAfterWakeup
        self.end_SurveysPerDay: int = end_SurveysPerDay
        self.end_DelayMinutesBetweenSurveys: int = end_DelayMinutesBetweenSurveys


class LinkDeletionSettings(object):
    start_DeleteLinkAtSubscriptionDeadline: bool
    start_DeleteLinkTimer: bool
    start_DeleteDelayMinutes: int
    daily_DeleteLinkAtNewLink: bool
    daily_DeleteLinkTimer: bool
    daily_DeleteDelayMinutes: int
    end_DeleteLinkAtNewLink: bool
    end_DeleteLinkTimer: bool
    end_DeleteDelayMinutes: int

    def __init__(self,
                 start_DeleteLinkAtSubscriptionDeadline: bool,
                 start_DeleteLinkTimer: bool,
                 start_DeleteDelayMinutes: int,
                 daily_DeleteLinkAtNewLink: bool,
                 daily_DeleteLinkTimer: bool,
                 daily_DeleteDelayMinutes: int,
                 end_DeleteLinkAtNewLink: bool,
                 end_DeleteLinkTimer: bool,
                 end_DeleteDelayMinutes: int,
                 *args, **kwargs):
        self.start_DeleteLinkAtSubscriptionDeadline: bool = start_DeleteLinkAtSubscriptionDeadline
        self.start_DeleteLinkTimer: bool = start_DeleteLinkTimer
        self.start_DeleteDelayMinutes: int = start_DeleteDelayMinutes
        self.daily_DeleteLinkAtNewLink: bool = daily_DeleteLinkAtNewLink
        self.daily_DeleteLinkTimer: bool = daily_DeleteLinkTimer
        self.daily_DeleteDelayMinutes: int = daily_DeleteDelayMinutes
        self.end_DeleteLinkAtNewLink: bool = end_DeleteLinkAtNewLink
        self.end_DeleteLinkTimer: bool = end_DeleteLinkTimer
        self.end_DeleteDelayMinutes: int = end_DeleteDelayMinutes


class RandomTimeShiftSettings(object):
    daily_RandomTimeShiftMinutes: int
    end_RandomTimeShiftMinutes: int

    def __init__(self,
                 daily_RandomTimeShiftMinutes: int,
                 end_RandomTimeShiftMinutes: int,
                 *args, **kwargs):
        self.daily_RandomTimeShiftMinutes: int = daily_RandomTimeShiftMinutes
        self.end_RandomTimeShiftMinutes: int = end_RandomTimeShiftMinutes


class Urls(object):
    start_url: List[str]
    daily_url: List[str]
    end_url: List[List[str]]
    end_url_distribution: EndUrlDistribution

    def __init__(self,
                 start_url: List[str],
                 daily_url: List[str],
                 end_url: List[List[str]],
                 end_url_distribution: str,
                 *args, **kwargs):
        self.start_url: List[str] = start_url
        self.daily_url: List[str] = daily_url
        self.end_url: List[List[str]] = end_url
        self.end_url_distribution: EndUrlDistribution = EndUrlDistribution[end_url_distribution]


class Texts(object):
    welcome: str
    subscribe: str
    subscribe_early: str
    subscribe_late: str
    subscribe_already: str
    subscribe_wakeup_time: str
    subscribe_condition: str
    subscribe_timezone: str
    unsubscribe: str
    daily_reminder: str
    end_reminder: str
    survey_reply: str
    endSurveyReminder: str
    endSurveyReminderYes: str
    endSurveyReminderNo: str

    def __init__(self,
                 welcome: str,
                 subscribe: str,
                 subscribe_early: str,
                 subscribe_late: str,
                 subscribe_already: str,
                 subscribe_wakeup_time: str,
                 subscribe_condition: str,
                 subscribe_timezone: str,
                 unsubscribe: str,
                 daily_reminder: str,
                 end_reminder: str,
                 survey_reply: str,
                 endSurveyReminder: str,
                 endSurveyReminderYes: str,
                 endSurveyReminderNo: str,
                 *args, **kwargs):
        self.welcome: str = welcome
        self.subscribe: str = subscribe
        self.subscribe_early: str = subscribe_early
        self.subscribe_late: str = subscribe_late
        self.subscribe_already: str = subscribe_already
        self.subscribe_wakeup_time: str = subscribe_wakeup_time
        self.subscribe_condition: str = subscribe_condition
        self.subscribe_timezone: str = subscribe_timezone
        self.unsubscribe: str = unsubscribe
        self.daily_reminder: str = daily_reminder
        self.end_reminder: str = end_reminder
        self.survey_reply: str = survey_reply
        self.endSurveyReminder: str = endSurveyReminder
        self.endSurveyReminderYes: str = endSurveyReminderYes
        self.endSurveyReminderNo: str = endSurveyReminderNo


class Help(object):
    helpEnabled: bool
    help_text: str
    surveyCommandHelp: str

    def __init__(self,
                 helpEnabled: bool,
                 help_text: str,
                 surveyCommandHelp: str,
                 *args, **kwargs):
        self.helpEnabled: bool = helpEnabled
        self.help_text: str = help_text
        self.surveyCommandHelp: str = surveyCommandHelp


class Config(object):
    api_token: str
    subscription_start_date: datetime
    subscription_deadline: datetime
    daily_dates: List[datetime]
    daily_times: List[List[time]]
    end_dates: List[datetime]
    end_times: List[List[time]]
    useTimeZoneCalculation: bool
    useDayCalculation: bool
    dayCalculationSettings: DayCalculationSettings
    useTimeCalculation: bool
    timeCalculationSettings: TimeCalculationSettings
    linkDeletionSettings: LinkDeletionSettings
    randomTimeShiftSettings: RandomTimeShiftSettings
    endSurveyReminderEnabled: bool
    endSurveyReminderDelayHours: int
    participantsEnterCondition: bool
    urls: Urls
    surveyCommandEnabled: bool
    texts: Texts
    help: Help

    def __init__(self,
                 api_token: str,
                 subscription_start_date: str,
                 subscription_deadline: str,
                 daily_dates: List[str],
                 daily_times: List[List[str]],
                 end_dates: List[str],
                 end_times: List[List[str]],
                 useTimeZoneCalculation: bool,
                 useDayCalculation: bool,
                 dayCalculationSettings: dict,
                 useTimeCalculation: bool,
                 timeCalculationSettings: dict,
                 linkDeletionSettings: dict,
                 randomTimeShiftSettings: dict,
                 endSurveyReminderEnabled: bool,
                 endSurveyReminderDelayHours: int,
                 participantsEnterCondition: bool,
                 urls: dict,
                 surveyCommandEnabled: bool,
                 texts: dict,
                 help: dict,
                 *args, **kwargs):
        self.api_token: str = api_token
        self.subscription_start_date: datetime = datetime.strptime(subscription_start_date, "%Y-%m-%d %H:%M")
        self.subscription_deadline: datetime = datetime.strptime(subscription_deadline, "%Y-%m-%d %H:%M")
        self.daily_dates: List[datetime] = [datetime.fromisoformat(date_str) for date_str in daily_dates]
        self.daily_times: List[List[time]] = \
            [[time.fromisoformat(time_str) for time_str in time_list] for time_list in daily_times]
        self.end_dates: List[datetime] = [datetime.fromisoformat(date_str) for date_str in end_dates]
        self.end_times: List[List[time]] = \
            [[time.fromisoformat(time_str) for time_str in time_list] for time_list in end_times]
        self.useTimeZoneCalculation: bool = useTimeZoneCalculation
        self.useDayCalculation: bool = useDayCalculation
        self.dayCalculationSettings: DayCalculationSettings = DayCalculationSettings(**dayCalculationSettings)
        self.useTimeCalculation: bool = useTimeCalculation
        self.timeCalculationSettings: TimeCalculationSettings = TimeCalculationSettings(**timeCalculationSettings)
        self.linkDeletionSettings: LinkDeletionSettings = LinkDeletionSettings(**linkDeletionSettings)
        self.randomTimeShiftSettings: RandomTimeShiftSettings = RandomTimeShiftSettings(**randomTimeShiftSettings)
        self.endSurveyReminderEnabled: bool = endSurveyReminderEnabled
        self.endSurveyReminderDelayHours: int = endSurveyReminderDelayHours
        self.participantsEnterCondition: bool = participantsEnterCondition
        self.urls: Urls = Urls(**urls)
        self.surveyCommandEnabled: bool = surveyCommandEnabled
        self.texts: Texts = Texts(**texts)
        self.help: Help = Help(**help)
