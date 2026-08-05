class MasterNotFoundError(Exception):
    pass


class MasterInactiveError(Exception):
    pass


class OfferingNotFoundError(Exception):
    pass


class OfferingInactiveError(Exception):
    pass


class OfferingDoesNotBelongToMasterError(Exception):
    pass


class MasterScheduleUnavailableError(Exception):
    pass


class BookingInPastError(Exception):
    pass


class BookingOutsideWorkingHoursError(Exception):
    pass


class BookingTimeConflictError(Exception):
    pass


class BookingNotFoundError(Exception):
    pass