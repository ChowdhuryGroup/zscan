import stage_control
#import PyCapture2

stage = stage_control.VXMController(step_size=0.0254)

stage.move_absolute(0, 1000)

for i in range(20):
    input('Take picture, press Enter when ready to move...')
    stage.move_absolute((i+1)*220, 1000)


