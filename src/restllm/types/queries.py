from fastapi import Query

from ..redis.queries import SortingField

offset_query = Query(default=0, ge=0, description="Offset to use for resuling list. Can be used for pagination by starting with offset 0 and limit 10, then offset 10 and limit 20", examples=[0,10])
limit_query = Query(default=10, gt=0, description="Limit to how many results should be returned as a response", examples=[5, 10])
sorting_field_query = Query(default=SortingField.CREATED_AT, description="Field to use for sorting response", examples=[SortingField.CREATED_AT, SortingField.UPDATED_AT])
ascending_query = Query(default=True, description="Should response be sorting in ascending order?. Default is True", examples=[True, False])