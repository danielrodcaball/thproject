class BusinessError(Exception):
    message: str
    error_code: str

    def __init__(self, message: str, error_code: str) -> None:
        self.message = message
        self.error_code = error_code


class DinerWithOverlappingReservationError(BusinessError):
    error_code = '40901'

    def __init__(self, diner_id) -> None:
        self.diner_id = diner_id
        self.message = "Diner with id {id} has an overlapping reservation".format(id=self.diner_id)


class ReservationForAPastTimeError(BusinessError):
    error_code = '40902'

    def __init__(self, past_datetime) -> None:
        self.past_datetime = past_datetime
        self.message = "It is not possible to create a reservation for a past time ({})".format(past_datetime)


class TableCanNotHoldDinersQtyError(BusinessError):
    error_code = '40903'

    def __init__(self, table_capacity, diners_qty) -> None:
        self.table_capacity = table_capacity
        self.diners_qty = diners_qty
        self.message = "The selected table (capacity for {}) can not hold the amount of diners ({})".format(
            table_capacity,
            diners_qty
        )


class TableOccupiedError(BusinessError):
    error_code = '40904'

    def __init__(self, target_datetime) -> None:
        self.target_datetime = target_datetime
        self.message = "The selected table is occupied on the selected datetime ({})".format(target_datetime)


class RestaurantDoesntMatchAllDinersDietRestrictionsError(BusinessError):
    error_code = '40905'

    def __init__(self) -> None:
        self.message = "The restaurant doesn't match all diners diet restrictions"
