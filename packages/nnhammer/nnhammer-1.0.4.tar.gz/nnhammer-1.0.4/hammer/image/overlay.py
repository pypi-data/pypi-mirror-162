import SimpleITK as sitk
import color


def overlay(image, label_map, colormap=None, opacity=0.5):
    if colormap is None:
        colormap = [color.yellow, ]
    image = sitk.GetImageFromArray(image)
    label_map = sitk.GetImageFromArray(label_map)
    itk_colormap = list(colormap[0])
    for i in colormap[1:]:
        itk_colormap += list(i)

    overlay_image = sitk.LabelOverlay(image, label_map, opacity=opacity, colormap=itk_colormap)
    overlay_image = sitk.GetArrayFromImage(overlay_image)
    return overlay_image
