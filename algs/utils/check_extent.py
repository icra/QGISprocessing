def check_extent(layer, background):
    xMaxL = layer.extent().xMaximum()
    xMinL = layer.extent().xMinimum()
    yMaxL = layer.extent().yMaximum()
    yMinL = layer.extent().yMinimum()

    xMaxB = background.extent().xMaximum()
    xMinB = background.extent().xMinimum()
    yMaxB = background.extent().yMaximum()
    yMinB = background.extent().yMinimum()

    if xMaxL > xMaxB or xMinL < xMinB or yMaxL > yMaxB or yMinL < yMinB:
        return False
    else:
        return True