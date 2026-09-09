class ResultParser:
    """Interpret raw results based on event result type."""

    @staticmethod
    def parse(result_string, result_type_code):
        """
        Parse a raw result string into a numeric value.

        Args:
            result_string: The raw result (e.g., "04:36", "150", "125.5")
            result_type_code: The type code (TIME, REPS, WEIGHT, DISTANCE, POINTS)

        Returns:
            float: The parsed numeric value
        """
        if not result_string:
            return 0.0

        result_string = str(result_string).strip()

        if result_type_code == 'TIME':
            return ResultParser._parse_time(result_string)
        elif result_type_code == 'REPS':
            return float(int(result_string))
        elif result_type_code == 'WEIGHT':
            return float(result_string)
        elif result_type_code == 'DISTANCE':
            return float(result_string)
        elif result_type_code == 'POINTS':
            return float(int(result_string))
        else:
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
