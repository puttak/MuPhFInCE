#!/usr/bin/python

#FILE DESCRIPTION=======================================================
#~ Simple python script to enable some parametrization of the mesh
#~ creation for the case of film flow down an inclined plate
#~ (interFoam used as a solver)
#~ 
#~ - Adds a grading in z-direction to reduce the number of cells
#~ - number of cells is based on the dense block cell size (input)


#LICENSE================================================================
#  fblockMeshGen.py
#  
#  Copyright 2015 Martin Isoz <martin@Poctar>
#  
#  Th0s program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  Th0s program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with th0s program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  

#FUNCTION INTERFACE BLOCK
def fblockMeshGen(caseDir,												#need to specify case directory
	h0 		 = 0.4e-3,													#initial droplet height
	geomSize = [50e-3,60e-3,7e-3],										#width, length and height of the geometry (in m)
	cellSize = [1e-3,1e-3,0.2e-3],										#width, length and height of on cell in dense block (in m)
	spGrad 	 = 10,														#grading in zDir of sparse block
	mScale 	 = 1):

	#IMPORT BLOCK=======================================================
	import os
	import copy
	import math
	
	#===================================================================
	#							EDITABLE
	#===================================================================
	
	#-------------------------------------------------------------------
	# GEOMETRY DATA
	#-------------------------------------------------------------------
	
	# central point
	x0, y0, z0 				= 0.0, 0.0, 0.0
	
	#-------------------------------------------------------------------
	# mesh grading
	grDX, grDY, grDZ = 1.0, 1.0, 1.0									#grading in dense block
	grSX, grSY, grSZ = 1.0, 1.0, 1.0									#grading in sparse block
	
	
	#===================================================================
	#							DO NOT EDIT
	#===================================================================
	
	# get the dimensions of the whole geometry and one cell
	aG,lG,hG  = geomSize
	dA,dL,dH  = cellSize
	
	# auxiliary variables for geometry creation
	hDCoeff   = 1.2														#how h0gh should the dense block be (relative to inlet height)
	zCoordVec = [z0,z0+hDCoeff*h0,z0+hG]						    	#levels in z direction
	nLrs   	  = len(zCoordVec)										    #number of levels in z direction
	
	# get the number of cells in each direction
	# Note: number of cells in zDir is based on input height
	nCellsX,nCellsY,nCellsZ = math.ceil(lG/dL),math.ceil(aG/dA),math.ceil(hDCoeff*h0/dH)
	# convert the number of cells to integers
	nCellsX,nCellsY,nCellsZ = int(nCellsX),int(nCellsY),int(nCellsZ)
	
	# auxiliary variables for mesh0ng
	nCellsZS   = int(math.ceil(2*(hG-hDCoeff*h0)/(dH*(1+spGrad))))		#get number of cells in sparse block
	# Note: grading factor in blockMesh is defined as the ratio of the
	#		last to first cell size (hjasak) -> I can get the number of
	#		cells from the sum of arithmetic series
	nCellsZVec = [nCellsZ,nCellsZS]										#vector with number of cells in zDir
	
	zGradVec   = [1.0,spGrad]
	
	# define matrix of vertices and nodes for arcs
	vert = []
	arcs = []															#not really used
	
	for zCoord in zCoordVec:											#th0s is quite simple
		vert.append([x0     ,y0    ,zCoord])
		vert.append([x0 + lG,y0     ,zCoord])
		vert.append([x0 + lG,y0 + aG,zCoord])
		vert.append([x0     ,y0 + aG,zCoord])

	lablsV = []															#list of vertices labels
	for i in range(nLrs):
		lablsV.append(range(0+i*4,4+i*4))
		
	for value in lablsV:
	    # Print each row's length and its elements.
	    print(value)
	
	#===================================================================

	#===================================================================
	#CREATE FILE AND WRITE THE DATA IN==================================
	bMD = open(caseDir + './constant/polyMesh/blockMeshDict','w')		#open file for writing
	
	#-----------------------------------------------------------------------
	# write the headline
	bMD.write('/*--------------------------------*- C++ -*----------------------------------*\ \n')
	bMD.write('| ========                 |                                                 | \n')
	bMD.write('| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           | \n')
	bMD.write('|  \\    /   O peration     | Version:  2.3.0                                 | \n')
	bMD.write('|   \\  /    A nd           | Web:      www.OpenFOAM.org                      | \n')
	bMD.write('|    \\/     M anipulation  |                                                 | \n')
	bMD.write('\*---------------------------------------------------------------------------*/ \n')
	
	# write file description
	bMD.write('FoamFile \n')
	bMD.write('{ \n \t version \t 2.0; \n \t format \t ascii; \n')
	bMD.write(' \t class \t\t dictionary; \n \t location \t "constant/polyMesh";\n \t object \t blockMeshDict; \n} \n')
	bMD.write('// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * // \n\n')
	
	#-------------------------------------------------------------------
	# convert to metres
	bMD.write('convertToMeters \t' + repr(mScale) + '; \n\n')
	
	#-------------------------------------------------------------------
	# write vertices
	bMD.write('vertices \n( \n')
	k = 0
	for row in vert:
	    bMD.write('\t ( ' + ' '.join(str(e) for e in row) + ' )\t//' + repr(k) + '\n')
	    k = k+1
	bMD.write('); \n\n')
	
	# write edges
	bMD.write('edges \n( \n')
	bMD.write('); \n\n')
	#~ 
	# write blocks
	bMD.write('blocks \n( \n')
	for i in range(nLrs-1):
		bMD.write('\t hex \n')
		bMD.write('\t \t ( '
				  +
				  ' '.join(str(e) for e in lablsV[i])
				  + ' ' + 
				  ' '.join(str(e) for e in lablsV[i+1])
				  +
				  ' ) \n'
				  )
		bMD.write('\t \t ( ' + repr(nCellsX) + ' ' + repr(nCellsY) + ' ' + repr(nCellsZVec[i]) + ' ) ')
		bMD.write('\t simpleGrading ')
		bMD.write('\t ( ' + repr(1.0) + ' ' + repr(1.0) + ' ' + repr(zGradVec[i]) + ' ) \n')
	bMD.write('); \n\n')
	
	# write boundaries
	bMD.write('boundary \n( \n')
	# -- plate
	bMD.write('\tplate \n\t{ \n')
	bMD.write('\ttype wall; \n')
	bMD.write('\tfaces \n \t(\n')
	wrVec = lablsV[0]
	bMD.write('\t\t( ' 
		 + 
		 ' '.join(str(e) for e in wrVec) 
		 + 
		 ' ) \n'
			 )            
	bMD.write('\t);\n\t} \n\n')
	# -- sides
	bMD.write('\tsides \n\t{ \n')
	bMD.write('\ttype wall; \n')
	bMD.write('\tfaces \n \t(\n')
	for i in range(nLrs-1):
		wrVec = []#front and back (in x-direction) are always non-empty
		wrVec.append([#not exactly top notch programming, but it should be clear what I did
					lablsV[i][0],
					lablsV[i+1][0],
					lablsV[i+1][-1],
					lablsV[i][-1],
				])
		wrVec.append([#not exactly top notch programming, but it should be clear what I did
					lablsV[i][1],
					lablsV[i+1][1],
					lablsV[i+1][-2],
					lablsV[i][-2],
				])    
		if nCellsY > 1:#left and right side are non-empty only for 3D meshes
				wrVec.append([#not exactly top notch programming, but it should be clear what I did
							lablsV[i][0],
							lablsV[i+1][0],
							lablsV[i+1][1],
							lablsV[i][1],
						])
				wrVec.append([#not exactly top notch programming, but it should be clear what I did
							lablsV[i][-1],
							lablsV[i+1][-1],
							lablsV[i+1][-2],
							lablsV[i][-2],
						])
		for wr in wrVec:
			bMD.write('\t\t( ' 
				 + 
				 ' '.join(str(e) for e in wr) 
				 + 
				 ' ) \n'
				 )            
	bMD.write('\t);\n\t} \n\n')
	# -- atmosphere
	bMD.write('\tatmosphere \n\t{ \n')
	bMD.write('\ttype patch; \n')
	bMD.write('\tfaces \n \t(\n')
	wrVec = lablsV[-1]
	bMD.write('\t\t( ' 
		 + 
		 ' '.join(str(e) for e in wrVec) 
		 + 
		 ' ) \n'
		 )            
	bMD.write('\t);\n\t} \n\n')
	#~ # -- emptyDirs
	
	bMD.write('); \n\n')
	
	bMD.write('mergePatchPairs \n( \n')
	bMD.write('); \n\n')
	#-------------------------------------------------------------------
	# footline
	bMD.write('// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * // \n\n')
	#-------------------------------------------------------------------
	# close file
	bMD.close()

	return;
