"""Tests for report.utils.dates module"""
import pytest
from datetime import datetime, date, timedelta

from report.utils.dates import (
    today_range,
    yesterday_range,
    this_week_range,
    last_week_range,
    custom_range,
    last_n_days_range,
    month_range,
)


class TestTodayRange:
    """Test today_range function"""
    
    def test_today_range_returns_tuple(self):
        start, end = today_range()
        assert isinstance(start, datetime)
        assert isinstance(end, datetime)
    
    def test_today_range_same_day(self):
        start, end = today_range()
        assert start.date() == end.date() == date.today()
    
    def test_today_range_full_day(self):
        start, end = today_range()
        assert start.hour == 0 and start.minute == 0 and start.second == 0
        assert end.hour == 23 and end.minute == 59 and end.second == 59


class TestYesterdayRange:
    """Test yesterday_range function"""
    
    def test_yesterday_range_returns_tuple(self):
        start, end = yesterday_range()
        assert isinstance(start, datetime)
        assert isinstance(end, datetime)
    
    def test_yesterday_range_correct_day(self):
        start, end = yesterday_range()
        expected_day = date.today() - timedelta(days=1)
        assert start.date() == end.date() == expected_day
    
    def test_yesterday_range_full_day(self):
        start, end = yesterday_range()
        assert start.hour == 0 and start.minute == 0 and start.second == 0
        assert end.hour == 23 and end.minute == 59 and end.second == 59


class TestThisWeekRange:
    """Test this_week_range function"""
    
    def test_this_week_range_returns_tuple(self):
        start, end = this_week_range()
        assert isinstance(start, datetime)
        assert isinstance(end, datetime)
    
    def test_this_week_range_starts_monday(self):
        start, end = this_week_range()
        assert start.weekday() == 0  # Monday
    
    def test_this_week_range_ends_sunday(self):
        start, end = this_week_range()
        assert end.weekday() == 6  # Sunday
    
    def test_this_week_range_spans_7_days(self):
        start, end = this_week_range()
        delta = end.date() - start.date()
        assert delta.days == 6  # 7 days (inclusive)


class TestLastWeekRange:
    """Test last_week_range function"""
    
    def test_last_week_range_returns_tuple(self):
        start, end = last_week_range()
        assert isinstance(start, datetime)
        assert isinstance(end, datetime)
    
    def test_last_week_range_starts_monday(self):
        start, end = last_week_range()
        assert start.weekday() == 0  # Monday
    
    def test_last_week_range_ends_sunday(self):
        start, end = last_week_range()
        assert end.weekday() == 6  # Sunday
    
    def test_last_week_range_before_this_week(self):
        last_start, last_end = last_week_range()
        this_start, this_end = this_week_range()
        
        assert last_end < this_start
    
    def test_last_week_range_spans_7_days(self):
        start, end = last_week_range()
        delta = end.date() - start.date()
        assert delta.days == 6


class TestCustomRange:
    """Test custom_range function"""
    
    def test_custom_range_valid_dates(self):
        start, end = custom_range("2024-01-01", "2024-01-31")
        
        assert start.date() == date(2024, 1, 1)
        assert end.date() == date(2024, 1, 31)
    
    def test_custom_range_same_day(self):
        start, end = custom_range("2024-01-15", "2024-01-15")
        
        assert start.date() == end.date() == date(2024, 1, 15)
    
    def test_custom_range_invalid_format(self):
        with pytest.raises(ValueError, match="Invalid date format"):
            custom_range("01-01-2024", "31-01-2024")
    
    def test_custom_range_start_after_end(self):
        with pytest.raises(ValueError, match="Start date must be before"):
            custom_range("2024-01-31", "2024-01-01")
    
    def test_custom_range_full_days(self):
        start, end = custom_range("2024-01-01", "2024-01-31")
        
        assert start.hour == 0 and start.minute == 0
        assert end.hour == 23 and end.minute == 59


class TestLastNDaysRange:
    """Test last_n_days_range function"""
    
    def test_last_n_days_range_7_days(self):
        start, end = last_n_days_range(7)
        
        assert isinstance(start, datetime)
        assert isinstance(end, datetime)
        assert end.date() == date.today()
        
        delta = end.date() - start.date()
        assert delta.days == 6  # 7 days inclusive
    
    def test_last_n_days_range_1_day(self):
        start, end = last_n_days_range(1)
        
        # Should be same as today_range
        assert start.date() == end.date() == date.today()
    
    def test_last_n_days_range_30_days(self):
        start, end = last_n_days_range(30)
        
        delta = end.date() - start.date()
        assert delta.days == 29  # 30 days inclusive
    
    def test_last_n_days_range_invalid_days(self):
        with pytest.raises(ValueError, match="Days must be at least 1"):
            last_n_days_range(0)
        
        with pytest.raises(ValueError, match="Days must be at least 1"):
            last_n_days_range(-5)


class TestMonthRange:
    """Test month_range function"""
    
    def test_month_range_january(self):
        start, end = month_range(2024, 1)
        
        assert start.date() == date(2024, 1, 1)
        assert end.date() == date(2024, 1, 31)
    
    def test_month_range_february_leap_year(self):
        start, end = month_range(2024, 2)
        
        assert start.date() == date(2024, 2, 1)
        assert end.date() == date(2024, 2, 29)  # Leap year
    
    def test_month_range_february_non_leap_year(self):
        start, end = month_range(2023, 2)
        
        assert start.date() == date(2023, 2, 1)
        assert end.date() == date(2023, 2, 28)
    
    def test_month_range_december(self):
        start, end = month_range(2024, 12)
        
        assert start.date() == date(2024, 12, 1)
        assert end.date() == date(2024, 12, 31)
    
    def test_month_range_invalid_month(self):
        with pytest.raises(ValueError, match="Month must be between 1 and 12"):
            month_range(2024, 0)
        
        with pytest.raises(ValueError, match="Month must be between 1 and 12"):
            month_range(2024, 13)
    
    def test_month_range_full_days(self):
        start, end = month_range(2024, 6)
        
        assert start.hour == 0 and start.minute == 0
        assert end.hour == 23 and end.minute == 59
