import os
from groclient import GroClient

API_HOST = "api.gro-intelligence.com"

from grocropclient.constants import FrequencyList, OtherItemsList, SourceList, MetricList, CropList, GRO_YIELD_MODELS

from fuzzywuzzy import fuzz
API_HOST = "api.gro-intelligence.com"

from grocropclient import crop_budgets

from typing_extensions import Literal
from enum import Enum
from datetime import datetime

AVAILABLE_SOURCES = [s.value for s in SourceList]
AVAILABLE_METRICS = [s.value for s in MetricList]
AVAILABLE_ITEMS   = [s.value for s in CropList] + [s.value for s in OtherItemsList]

AVAILABLE_METRICS_NAMES = [(s.value, s.name.replace('_', ' ')) for s in MetricList]
AVAILABLE_ITEMS_NAMES   = [(s.value, s.name.replace('_', ' ')) for s in CropList] + [(s.value, s.name.replace('_', ' ')) for s in OtherItemsList]

# Returns True if the source/item/metric selection is within the US Crop tier.
def is_valid_selection(dataseries):
    return dataseries['source_id'] in AVAILABLE_SOURCES and \
    dataseries['metric_id'] in AVAILABLE_METRICS and \
    dataseries['item_id'] in AVAILABLE_ITEMS

# Return the number of days between today's data and a Gro date.
def days_ago(gro_date):
    # Wer remove the TZ ([0:10]) before we parse.
    return (datetime.today() - datetime.strptime(gro_date[0:10], "%Y-%m-%d")).days


# Translate ENUM into their value when inside a dictionary.
# This is useful when using methods that take ids as input, e.g. get_data_series.
def handle_enums(obj):
  fix_enum = lambda x: x.value if isinstance(x, Enum) else x
  for k,v in obj.items():
    obj[k] = list(map(fix_enum, v)) if isinstance(v, list) else fix_enum(v)
  return obj


class GroCropClient(object):

    def __init__(self, api_host=API_HOST, access_token=None):
        """Construct a GroClimateClient instance.
        Parameters
        ----------
        api_host : string, optional
            api_host : string
            The API host's url, excluding 'https://', to be consistent with groclient/lib.py
            ex. 'api.gro-intelligence.com'
        access_token : string, optional
            Your Gro API authentication token. If not specified, the
            :code:`$GROAPI_TOKEN` environment variable is used. See
            :doc:`authentication`.
        Raises
        ------
            RuntimeError
                Raised when neither the :code:`access_token` parameter nor
                :code:`$GROAPI_TOKEN` environment variable are set.
        Examples
        --------
            >>> client = GroClient()  # token stored in $GROAPI_TOKEN
            >>> client = GroClient(access_token="your_token_here")
        """

        if access_token is None:
            access_token = os.environ.get("GROAPI_TOKEN")
            if access_token is None:
                raise RuntimeError("GROAPI_TOKEN environment variable must be set when "
                                   "Your Gro Client is constructed without the access_token argument")
        self._api_host = api_host
        self._access_token = access_token
        self._client = GroClient(self._api_host, self._access_token)

    def get_sources(self):
        """Returns a list of all US Crop sources, as JSON.
            The schema for our climate sources is:
            ['description',
            'fileFormat',
            'historicalStartDate',
            'id',
            'language',
            'longName',
            'name',
            'regionalCoverage',
            'resolution',
            'sourceLag']
        """
        dict = self._client.lookup('sources', [s.value for s in SourceList])
        return list(dict.values())

    def get_metrics(self, with_details=False):
        """Returns a list of metrics supported by the US Crop API.
           The list of id's comes from MetricList.
           For each item, we fetch the data from the Gro API via `lookup` if with_details is True. 
        """
        if with_details:
            return [self._client.lookup("metrics", m.value) for m in MetricList]
        else:
            return [{"short_name": m.name, "id": m.value} for m in MetricList]

    def get_crops(self, with_details=False):
        """Returns a list of metrics supported by the US Crop API.
           The list of id's comes from CropList.
           For each item, we fetch the data from the Gro API via `lookup` if with_details is True
        """
        if with_details:
            return [self._client.lookup("items", c.value) for c in CropList]
        else:
            return [{"short_name": c.name, "id": c.value} for c in CropList]

    # CROP BUDGET functions

    def get_crop_budgets(self, crop='', state=''):
        return crop_budgets.get_all_crop_budgets(self._api_host, self._access_token, crop=crop, state=state)

    def get_crop_budget_as_df(self, source_name, item_name, region_name):
        return crop_budgets.get_crop_budget_as_df(self._api_host, self._access_token, source_name=source_name, item_name=item_name, region_name=region_name)

    # END OF CROP BUDGET functions

    def lookup(self, entity_type, entity_ids):
        return self._client.lookup(entity_type, entity_ids)

    def lookup_unit_abbreviation(self, unit_id):
        return self.lookup("units", unit_id)["abbreviation"]

    def find_data_series(self, **kwargs):
        """Find data series from the US Crop tier matching a combination of entities specified by
        name and yield them ranked by coverage.
        Parameters
        ----------
        metric : string, optional
        item : string, optional
        region : string, optional
        partner_region : string, optional
        start_date : string, optional
            YYYY-MM-DD
        end_date : string, optional
            YYYY-MM-DD
        e.g. dataseries_gen = client.find_data_series(item="corn", metric="planted area", region="Illinois")
            for i in range(5):
            print(next(dataseries_gen))
        """

        dataseries_gen = self._client.find_data_series(**kwargs)
        while True:
            result = next(dataseries_gen)
            if is_valid_selection(result):
                yield result


    def get_data_series(self, **kwargs):
        """Get available data series for the given selections from the US Crop tier.
        https://developers.gro-intelligence.com/data-series-definition.html
        Parameters
        ----------
        metric_id : integer, optional
        item_id : integer, optional
        region_id : integer, optional
        partner_region_id : integer, optional
        source_id : integer, optional
        frequency_id : integer, optional
        Returns
        -------
        list of dicts
            Example::
                [{ 'metric_id': 2020032, 'metric_name': 'Seed Use',
                    'item_id': 274, 'item_name': 'Corn',
                    'region_id': 1215, 'region_name': 'United States',
                    'source_id': 24, 'source_name': 'USDA FEEDGRAINS',
                    'frequency_id': 7,
                    'start_date': '1975-03-01T00:00:00.000Z',
                    'end_date': '2018-05-31T00:00:00.000Z'
                }, { ... }, ... ]
        """

        # We translate ENUMs if needed.
        kwargs = handle_enums(kwargs)

        dataseries = self._client.get_data_series(**kwargs)

        filtered_dataseries=[series for series in dataseries if is_valid_selection(series)]
        return filtered_dataseries

    def get_data_points(self, **selections):
        """Gets all the data points for a given selection within the climate tier.
        Parameters
        ----------
        metric_id : integer or list of integers
            How something is measured. e.g. "Export Value" or "Area Harvested"
        item_id : integer or list of integers
            What is being measured. e.g. "Corn" or "Rainfall"
        region_id : integer or list of integers
            Where something is being measured e.g. "United States Corn Belt" or "China"
        partner_region_id : integer or list of integers, optional
            partner_region refers to an interaction between two regions, like trade or
            transportation. For example, for an Export metric, the "region" would be the exporter
            and the "partner_region" would be the importer. For most series, this can be excluded
            or set to 0 ("World") by default.
        source_id : integer
        frequency_id : integer
        unit_id : integer, optional
        start_date : string, optional
            All points with end dates equal to or after this date
        end_date : string, optional
            All points with start dates equal to or before this date
        reporting_history : boolean, optional
            False by default. If true, will return all reporting history from the source.
        complete_history : boolean, optional
            False by default. If true, will return complete history of data points for the selection. This will include
            the reporting history from the source and revisions Gro has captured that may not have been released with an official reporting_date.
        insert_null : boolean, optional
            False by default. If True, will include a data point with a None value for each period
            that does not have data.
        at_time : string, optional
            Estimate what data would have been available via Gro at a given time in the past. See
            :sample:`at-time-query-examples.ipynb` for more details.
        include_historical : boolean, optional
            True by default, will include historical regions that are part of your selections
        available_since : string, optional
            Fetch points since last data retrieval where available date is equal to or after this date
        """

        # We translate ENUMS if any.
        selections = handle_enums(selections)

        # Check that source is within tier.
        if 'source_id' not in selections:
            raise Exception('a valid source_id MUST be selected')
        if selections['source_id'] not in AVAILABLE_SOURCES:
            raise Exception('Source %d is not part of the US Crops tier' % selections['source_id'])


        # For items and metrics, we may receive a list as an input.
        # In such cases, we interset the list with the list of valid metrics (resp. items),
        # If the intersection is non-empty, we proceed.

        # Check that item is within tier.
        if 'item_id' not in selections:
            raise Exception('a valid item_id MUST be selected')
        item_id = selections["item_id"]
        if ((type(item_id) == list) and len(set(item_id) & set(AVAILABLE_ITEMS)) == 0) or \
            item_id not in AVAILABLE_ITEMS:
            raise Exception('Selected item(s) %s not part of the US Crops tier' % str(selections['item_id']))

        # Check that metric is within tier.
        if 'metric_id' not in selections:
            raise Exception('a valid metric_id MUST be selected')
        metric_id = selections["metric_id"]
        if ((type(metric_id) == list) and len(set(metric_id) & set(AVAILABLE_METRICS)) == 0) or \
            metric_id not in AVAILABLE_METRICS:
            raise Exception('Selected metrics(s) %s not part of the US Crops tier' % str(selections['metric_id']))

        return self._client.get_data_points(**selections)

    def get_ancestor_regions(
      self,
      entity_id,
      distance=None,
      include_details=True,
      ancestor_level=None,
      include_historical=True,
      ):
        """Given a region, returns all its ancestors i.e.
        regions that "contain" in the given region.
        Parameters
        ----------
        entity_id : integer
        distance: integer, optional
            Return all entities that contain the entity_id at maximum distance. If provided along
            with `ancestor_level`, this will take precedence over `ancestor_level`.
            If not provided, get all ancestors.
        include_details : boolean, optional
            True by default. Will perform a lookup() on each ancestor to find name,
            definition, etc. If this option is set to False, only ids of ancestor
            entities will be returned, which makes execution significantly faster.
        ancestor_level : integer, optional
            The region level of interest. See REGION_LEVELS constant. This should only be specified
            if the `entity_type` is 'regions'. If provided along with `distance`, `distance` will
            take precedence. If not provided, and `distance` not provided, get all ancestors.
        include_historical : boolean, optional
            True by default. If False is specified, regions that only exist in historical data
            (e.g. the Soviet Union) will be excluded.
        """
        return self._client.get_ancestor(
            'regions', entity_id,
            distance=distance, include_details=include_details,
            ancestor_level=ancestor_level, include_historical=include_historical)

    def get_descendant_regions(
        self,
        entity_id,
        distance=None,
        include_details=True,
        descendant_level=None,
        include_historical=True,
    ):
        """Given a region, returns all its descendants i.e. entities that are "contained" in the given region.
        The `distance` parameter controls how many levels of child entities you want to be returned.
        Additionally, if you are getting the descendants of a given region, you can specify the
        `descendant_level`, which will return only the descendants of the given `descendant_level`.
        However, if both parameters are specified, `distance` takes precedence over
        `descendant_level`.
        Parameters
        ----------
        entity_id : integer
        distance: integer, optional
            Return all entities that contain the entity_id at maximum distance. If provided along
            with `descendant_level`, this will take precedence over `descendant_level`.
            If not provided, get all ancestors.
        include_details : boolean, optional
            True by default. Will perform a lookup() on each descendant  to find name,
            definition, etc. If this option is set to False, only ids of descendant
            entities will be returned, which makes execution significantly faster.
        descendant_level : integer, optional
            The region level of interest. See REGION_LEVELS constant. This should only be specified
            if the `entity_type` is 'regions'. If provided along with `distance`, `distance` will
            take precedence. If not provided, and `distance` not provided, get all ancestors.
        include_historical : boolean, optional
            True by default. If False is specified, regions that only exist in historical data
            (e.g. the Soviet Union) will be excluded.
        """
        return self._client.get_descendant(
            'regions', entity_id,
            distance=distance, include_details=include_details,
            descendant_level=descendant_level, include_historical=include_historical)

    def get_geo_centre(self, region_id):
        """Given a region_id (int), returns the geographic centre in degrees lat/lon.
        """
        return self._client.get_geo_centre(region_id)

    def get_geojson(self, region_id, zoom_level=7):
        """Given a region ID, return shape information in geojson.
        """
        return self._client.get_geojson(region_id, zoom_level=zoom_level)

    def search(self, entity_type, search_terms, num_results=10):
        """Searches for the given search term. Better matches appear first.
        Search for the given search terms and look up their details.
        For each result, yield a dict of the entity and its properties.
        """
        if entity_type == 'regions':
            for result in self._client.search_and_lookup('regions', search_terms, num_results=num_results):
                yield result

        if entity_type == 'metrics':
            ranked_results = sorted( [ (k[0], k[1], fuzz.token_set_ratio(search_terms, k[1])) for k in AVAILABLE_METRICS_NAMES], key=lambda x:x[2], reverse=True)
            for result in ranked_results:
                yield { 'metric_id': result[0], 'metric_shortname': result[1], 'score': result[2] }

        if entity_type == 'items':
            ranked_results = sorted([(k[0], k[1], fuzz.token_set_ratio(search_terms, k[1])) for k in AVAILABLE_METRICS_NAMES], key=lambda x:x[2], reverse=True)
            for result in ranked_results:
                yield { 'item_id': result[0], 'item_shortname': result[1], 'score': result[2] }

        return "N/A"

    def get_top_region_match(self, query: str) -> dict:
        """
        Simple wrapper for self.search(...), returns the top region match for a string query
        """
        searchResults=list(self.search('regions', query, num_results=1))

        if len(searchResults)==0:
            raise Exception("No region match for query "+query)
        return searchResults[0]

    def add_single_data_series(self, data_series: dict) -> None:
        """Save a data series object to the GroClient's data_series_list.
        For use with :meth:`~.get_df`.
        Parameters
        ----------
        data_series : dict
            A single data_series object, as returned by :meth:`~.get_data_series` or
            :meth:`~.find_data_series`.
            See https://developers.gro-intelligence.com/data-series-definition.html
        Returns
        -------
        None
        """
        if is_valid_selection(data_series) is False:
            raise Exception("Can't add the following data series, not in the US Crops tier: "+str(data_series))
        self._client.add_single_data_series(data_series)

    def clear_data_series_list(self) -> None:
        """
        Clear the list of saved data series which have been added with add_single_data_series(...)
        """
        self._client._data_series_list = set()
        self._client._data_series_queue = []
        self._client._data_frame = pandas.DataFrame()

    def get_df(self, **kwargs):
        """Call :meth:`~.get_data_points` for each saved data series and return as a combined
        dataframe.
        Note you must have first called either :meth:`~.add_data_series` or
        :meth:`~.add_single_data_series` to save data series into the GroClient's data_series_list.
        You can inspect the client's saved list using :meth:`~.get_data_series_list`.
        See https://developers.gro-intelligence.com/api.html#groclient.GroClient.get_df for full documentation
        """

        return self._client.get_df(**kwargs)

######################################
########## HELPER FUNCTIONS ##########
######################################

    ###########
    ## Yield ##
    ###########

    def get_all_yield_models():
        return [{"id": k, "name": "%s / %s" % (v["region_name"], v["item_name"])} for k,v, in GRO_YIELD_MODELS.items()]

    def get_yield_model_data(self, yield_model_id, start_date=None):
        if yield_model_id not in GRO_YIELD_MODELS:
            raise Exception("Not a valid yield model")
        else:
            ym = GRO_YIELD_MODELS[yield_model_id]
            # We need to ask for revisions to get all daily predictions.
            # We need to ask for metadata to get the confidence interval value.
            params = { "show_revisions": True, "show_metadata": True,
                       "source_id": SourceList.GRO_YIELD_MODEL, "frequency_id": 9,
                       "item_id":  ym["item_id"], "region_id": ym["region_id"], "metric_id": ym["metric_id"]}
        if start_date:
            params["start_date"] = start_date
        return self.get_data_points(**params)

    def get_yield_model_summary_last_N_days(self, yield_model_data, N:int = 5):
        if len(yield_model_data) == 0:
            print("no data")
            return None
        unit_id = yield_model_data[0]['unit_id']
        unit_abbrev = self.lookup_unit_abbreviation(unit_id)
        return [ { "date": k["available_date"][0:10],
                   "value": "%f ± %f (%s)" % (k["value"],
                   k["metadata"]["conf_interval"], unit_abbrev)} for k in yield_model_data \
                if days_ago(k["available_date"]) < N][::-1]

    ############
    ## Prices ##
    ############

    def get_cash_prices_spot_county_level(self, crop_id, county_id):
        params = { "source_id": SourceList.DTN_DISTRICT_AGGREGATED,
                   "frequency_id": 1,
                   "item_id":  crop_id,
                   "region_id": county_id,
                   "metric_id": MetricList.CASH_PRICES_SPOT_DELIVERY_CLOSE
                }
        return self.get_data_points(**params)

    def get_cash_prices_new_crop_county_level(self, crop_id, county_id):
        params = { "source_id": SourceList.DTN_DISTRICT_AGGREGATED,
                   "frequency_id": 1,
                   "item_id":  crop_id,
                   "region_id": county_id,
                   "metric_id": MetricList.CASH_PRICES_NEW_CROP_DELIVERY_CLOSE
                }
        return self.get_data_points(**params)

    def get_basis_prices_spot_county_level(self, crop_id, county_id):
        params = { "source_id": SourceList.DTN_DISTRICT_AGGREGATED,
            "frequency_id": 1,
            "item_id":  crop_id,
            "region_id": county_id,
            "metric_id": MetricList.BASIS_PRICES_SPOT_DELIVERY_CLOSE
            }
        return self.get_data_points(**params)

    def get_basis_prices_new_crop_county_level(self, crop_id, county_id):
        params = { "source_id": SourceList.DTN_DISTRICT_AGGREGATED,
            "frequency_id": 1,
            "item_id":  crop_id,
            "region_id": county_id,
            "metric_id": MetricList.BASIS_PRICES_NEW_CROP_DELIVERY_CLOSE
            }
        return self.get_data_points(**params)

    def get_futures_prices_rolling_front_month_settle_national(self, crop_id):
        params = { "source_id": SourceList.GRO_DERIVED,
            "frequency_id": 1,
            "item_id":  crop_id,
            "region_id": 1215,
            "metric_id": MetricList.FUTURES_PRICES_ROLLING_FRONT_MONTH_SETTLE
            }
        return self.get_data_points(**params)      

    def get_futures_prices_settle_national(self, crop_id):
        params = { "source_id": SourceList.CME,
            "frequency_id": 15,
            "item_id":  crop_id,
            "region_id": 1215,
            "metric_id": MetricList.FUTURES_PRICES_SETTLE
            }
        return self.get_data_points(**params)      

    ##########
    ## Area ##
    ##########

    def get_area_harvested_USDA(self, crop: CropList, region):
        params = { "metric_id": MetricList.AREA_HARVESTED,
             "item_id": crop,
             "region_id": region,
             "source_id": SourceList.USDA_NASS,
             "frequency_id": 9}
        return self.get_data_points(**params)

    def get_area_harvested_GroForecasts(self, crop: CropList, region):
        params = { "metric_id": MetricList.AREA_HARVESTED,
             "item_id": crop,
             "region_id": region,
             "source_id": SourceList.GRO_FORECASTS,
             "frequency_id": 9}
        return self.get_data_points(**params)
  
    def get_area_planted_USDA(self, crop: CropList, region):
         params = { "metric_id": MetricList.AREA_PLANTED,
             "item_id": crop,
             "region_id": region,
             "source_id": SourceList.USDA_NASS if crop in [CropList.CORN, CropList.SOYBEANS] else SourceList.USDA_FSA,
             "frequency_id": 9}
         return self.get_data_points(**params)

    def get_area_planted_GroForecasts(self, crop: CropList, region):
        params = { "metric_id": MetricList.AREA_PLANTED,
             "item_id": crop,
             "region_id": region,
             "source_id": SourceList.GRO_ENTERPRISE,
             "frequency_id": 9}
        return self.get_data_points(**params)

    def get_area_prevented_USDA(self, crop: CropList, region, non_irrigated=False):
        params = { "metric_id": MetricList.AREA_PREVENTED_NON_IRRIGATED if non_irrigated else MetricList.AREA_PREVENTED,
             "item_id": crop,
             "region_id": region,
             "source_id": SourceList.USDA_FSA,
             "frequency_id": 9}
        return self.get_data_points(**params)

    def get_area_prevented_GroForecasts(self, crop: CropList, region, non_irrigated=False):
        params = { "metric_id": MetricList.AREA_PREVENTED_NON_IRRIGATED if non_irrigated else MetricList.AREA_PREVENTED,
             "item_id": crop.value,
             "region_id": region,
             "source_id": SourceList.GRO_ENTERPRISE,
             "frequency_id": 9}
        return self.get_data_points(**params)

    def get_planting_progress(self, crop: CropList, region):
        params = {'metric_id': MetricList.PLANTING_PROGRESS, 
	            'item_id': crop, 
            	'region_id': region, 
	            'partner_region_id': 0, 
	            'source_id': SourceList.USDA_NASS_CROPS, 
	            'frequency_id': 2
                }
        return self.get_data_points(**params)

    ###########
    ## Trade ##
    ###########
    def get_sales_qty_outstanding_NMY(self, crop: CropList, partner_region=1231):
        params = { 'metric_id': MetricList.SALES_QUANTITY_OUTSTANDING_NMY,
	               'item_id': crop, 
	               'region_id': 1215, 
	               'partner_region_id': partner_region, 
	               'source_id': SourceList.USDA_ESR, 
	               'frequency_id': 2, 
	                'unit_id': 14
                    }
        return self.get_data_points(**params)

    def get_sales_qty_total_commitments(self, crop, partner_region=1231):
        params = { 'metric_id': MetricList.SALES_QUANTITY_TOTAL_COMMITMENTS_MASS,
	               'item_id': crop, 
	               'region_id': 1215, 
	               'partner_region_id': partner_region, 
	               'source_id': SourceList.USDA_ESR, 
	               'frequency_id': 2, 
	               'unit_id': 14
                   }
        return self.get_data_points(**params)

    #############
    ## Climate ##
    #############
    
    def get_Gro_Drought_Index(self, region_id, frequency, start_date=None):
        if isinstance(frequency, Enum):
            frequency = frequency.value
        if frequency not in [FrequencyList.DAILY.value, FrequencyList.WEEKLY.value, FrequencyList.MONTHLY.value]:
            raise Exception("Invalid frequency. Must be one of {daily, weekly, monthly}.")
        params = { "metric_id": 15852252, "item_id": 17388, "frequency_id": frequency, "source_id": 145,
                   "region_id": region_id }
        if start_date:
            params["start_date"] = start_date
        return self.get_data_points(**params)

    def get_Gro_Observed_Flood(self, region_id, start_date=None):
        params = { "metric_id": MetricList.OBSERVED_FLOOD, "item_id": OtherItemsList.WATER_AREAS,
                   "frequency_id": FrequencyList.DAILY, "source_id": SourceList.GRO_DERIVED_GEOSPATIAL,
                   "region_id": region_id }
        if start_date:
            params["start_date"] = start_date
        return self.get_data_points(**params)


    # TODO
    """"
    MODIS	NDVI_8day
    MODIS	LST_daily
    SMOS	SMOS_daily
	
    NCEP	GFS_tmax_daily_today
	        GFS_tmax_daily_yesterday
	        GFS_tmin_daily_today
	        GFS_tmin_daily_yesterday
    NCEP	GFS_precip_daily_today
	        GFS_precip_daily_yesterday
    """

