#!/usr/bin/python3

import os
import gdspy

orig_box_width=50.
orig_box_spacing=50.

layer_mapping = {
	'pwell' : [41],
	'nwell' : [42],
	'isolation' : [41,42],
	'metal1' : [49],
}

cellname='L500_MOSFET_aligning'

magic_script="\n"
magic_script+="drc off"
magic_script+="\n"
magic_script+="box 0 0 0 0"
magic_script+="\n"
magic_script+="tech load scmos"
magic_script+="\n"
magic_script+="load Layout/magic/"+cellname+".mag"
magic_script+="\n"
magic_script+="drc off"
magic_script+="\n"
magic_script+="gds readonly true"
magic_script+="\n"
magic_script+="gds rescale false"
magic_script+="\n"
magic_script+="load "+cellname
magic_script+="\n"
magic_script+="gds flatten yes"
magic_script+="\n"
magic_script+="gds label no"
magic_script+="\n"
magic_script+="gds merge yes"
magic_script+="\n"
magic_script+="gds write gds/"+cellname
magic_script+="\n"
magic_script+="calma write gds/"+cellname
magic_script+="\n"
magic_script+="quit -noprompt"
magic_script+="\n"

print(os.popen("mkdir -p gds").read())
print(os.popen("magic -dnull -noconsole << EOF"+magic_script+"EOF").read())

gdsii=gdspy.GdsLibrary()
gdsii.read_gds(
	"gds/"+cellname+".gds",
)
cell=gdsii.extract(cellname)
cell=cell.flatten()
bb=cell.get_bounding_box()
left_bottom=bb[0]
right_top=bb[1]
left_bottom_rect=gdspy.Rectangle(left_bottom-orig_box_spacing, left_bottom-orig_box_spacing-[orig_box_width,orig_box_width], 100)
right_top_rect=gdspy.Rectangle(right_top+orig_box_spacing, right_top+orig_box_spacing+[orig_box_width,orig_box_width], 100)
cell.add(left_bottom_rect)
cell.add(right_top_rect)
cell=cell.flatten()

for layername in layer_mapping:
	ncell=cell.copy(layername,deep_copy=True)
	ncell=ncell.flatten()
	for idx in ncell.get_layers():
		if not idx in layer_mapping[layername]:
			if idx != 100:
				ncell=ncell.remove_polygons(lambda pts, layer, datatype: layer == idx)
	ncell=ncell.flatten(single_layer=1)
	newgdsii=gdspy.GdsLibrary("mask_"+layername)
	newgdsii.add(ncell)
	newgdsii.write_gds("gds/mask_"+layername+".gds")
