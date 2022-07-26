import subprocess 
from opentrons import protocol_api, types
metadata = {'apiLevel': '2.9'} 
AUDIO_FILE_PATH = '/var/lib/jupyter/notebooks/JornsCave/SMILER_DISPATCHFX.mp3'  
def run_quiet_process(command): 
    subprocess.check_output('{} &> /dev/null'.format(command), shell=True) 
def test_speaker(): 
    print('Speaker') 
    try:
         run_quiet_process('mpg123 {}'.format(AUDIO_FILE_PATH))
    except KeyboardInterrupt:
         pass
         print()


def run(protocol: protocol_api.ProtocolContext):
    tr2 = protocol.load_labware('opentrons_96_tiprack_20ul', '1')
    p20 = protocol.load_instrument('p20_single_gen2', 'left', tip_racks=[tr2])
    p20.pick_up_tip()
    p20.drop_tip()
    test_speaker()
    
    
    
    
    
    