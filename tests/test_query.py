from ultru_client.utils.query import Query
from ultru_client.utils.record_types import Types
from ultru_client.utils.scores import Scores


def test_create_query_just_record_type():
    tmp_query = Query(record_type='process')
    assert tmp_query.body == {'record_type':'process'}

def test_create_query_recordtype_and_score():
    tmp_query = Query(record_type='process', score='benign')
    assert tmp_query.body == {'record_type': 'process', 'score_low': 0, 'score_high': 5}