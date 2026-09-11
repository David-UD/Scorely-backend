class ResultParser:
    """Interpret raw results into a numeric value.

    Results without a colon are numeric (REPS / WEIGHT / DISTANCE / POINTS).
    Results containing a colon are treated as time (MM:SS or HH:MM:SS).
    """

    @staticmethod
    def parse(result_string):
        """
        Parse a raw result string into a numeric value.

        Args:
            result_string: The raw result (e.g., "04:36", "150", "125.5")

        Returns:
            float: The parsed numeric value
        """
        if not result_string:
            return 0.0

        result_string = str(result_string).strip()

        if ':' in result_string:
            return ResultParser._parse_time(result_string)

        return float(result_string)

    @staticmethod
    def _parse_time(time_string):
        """Parse time string (MM:SS or HH:MM:SS) to seconds."""
        parts = time_string.split(':')
        if len(parts) == 2:
            minutes, seconds = parts
            return int(minutes) * 60 + int(seconds)
        elif len(parts) == 3:
            hours, minutes, seconds = parts
            return int(hours) * 3600 + int(minutes) * 60 + int(seconds)
        return float(time_string)
