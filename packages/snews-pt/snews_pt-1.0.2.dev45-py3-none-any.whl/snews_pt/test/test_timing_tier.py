"""Test publishing timing tier messages."""
from snews_pt.snews_pub import SNEWSTiersPublisher
from snews_pt.snews_pt_utils import set_name

def test_timing_expected():
    """Test with example of expected message type."""
    # Create timing tier message.
    set_name(detector_name="XENONnT")
    tims = SNEWSTiersPublisher(detector_name='XENONnT', neutrino_time='12/06/09 15:31:08:1098', timing_series=['12/06/09 15:31:08:1098', '12/06/09 15:33:07:8910'],
                               firedrill_mode=False)

    # Check that message has expected structure.
    assert tims.tiernames == ['CoincidenceTier', 'TimeTier']
    assert tims.message_data == {'detector_name': 'XENONnT', 'machine_time': None, 'neutrino_time': '12/06/09 15:31:08:1098', 'p_val': None, 'p_values': None,
                                 'timing_series': ['12/06/09 15:31:08:1098', '12/06/09 15:33:07:8910'], 'which_tier': None, 'n_retract_latest': None,
                                 'retraction_reason': None, 'detector_status': None, 'is_pre_sn': False, 't_bin_width': None, }

    input_messages = [{'detector_name': 'XENONnT', 'machine_time': None, 'neutrino_time': '12/06/09 15:31:08:1098',
                     'p_val': None, 'meta': {}, 'schema_version': '1.1.0'},
                      {'detector_name': 'XENONnT', 'machine_time': None,
                     'neutrino_time': '12/06/09 15:31:08:1098',
                       'timing_series': ['12/06/09 15:31:08:1098', '12/06/09 15:33:07:8910'],
                       'meta': {}, 'schema_version': '1.1.0'}]
    for i, message in enumerate(input_messages):
        for k,v in message.items():
            if k in ['sent_time', 'machine_time']:
                continue
            assert tims.messages[i][k] == v

    assert tims.env_file == None
    # Try to send message to SNEWS 2.0 server.
    try:
        tims.send_to_snews()
    except Exception as exc:
        print('SNEWSTiersPublisher.send_to_snews() test failed!\n')
        assert False, f"Exception raised:\n {exc}"
