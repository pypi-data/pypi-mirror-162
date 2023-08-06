# Duke-AI Development Package

This is a duke development package for the developers.

To know more about us can, you visit our [website](http://duke.ai/).



#### check_rate_con_schema: Checks the basic schema whether it is standardized schema or not.
```{r}
from dukeai.rpa_functions.ratecon_schema_check import check_rate_con_schema
check_rate_con_schema(rate_con_data, only_warning=False)
```

#### check_rate_con_data: Checks the minimum required data in the rate confirmation.
```{r}
from dukeai.rpa_functions.ratecon_data_check import check_rate_con_data
check_rate_con_data(rate_con_data)
```

#### Get the rate confirmation standardized schema
```{r}
from functions.get_ratecon_schema import get_rate_confirmation_schema, get_stops_schema, get_entity_schema
from functions.get_ratecon_schema import get_reference_schema, get_note_schema, get_dates_schema
```