# -*- coding: utf-8 -*-
'''
/**************************************************************************************************************************
 SemiAutomaticClassificationPlugin

 The Semi-Automatic Classification Plugin for QGIS allows for the supervised classification of remote sensing images, 
 providing tools for the download, the preprocessing and postprocessing of images.

							 -------------------
		begin				: 2012-12-29
		copyright		: (C) 2012-2021 by Luca Congedo
		email				: ing.congedoluca@gmail.com
**************************************************************************************************************************/
 
/**************************************************************************************************************************
 *
 * This file is part of Semi-Automatic Classification Plugin
 * 
 * Semi-Automatic Classification Plugin is free software: you can redistribute it and/or modify it under 
 * the terms of the GNU General Public License as published by the Free Software Foundation, 
 * version 3 of the License.
 * 
 * Semi-Automatic Classification Plugin is distributed in the hope that it will be useful, 
 * but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or 
 * FITNESS FOR A PARTICULAR PURPOSE. 
 * See the GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License along with 
 * Semi-Automatic Classification Plugin. If not, see <http://www.gnu.org/licenses/>. 
 * 
**************************************************************************************************************************/

'''



cfg = __import__(str(__name__).split('.')[0] + '.core.config', fromlist=[''])

class CloudMasking:

	def __init__(self):
		pass
		
		
	# value text changed
	def textChanged(self):		
		self.checkValueList()
		
	# check value list
	def checkValueList(self):
		try:
			# class value list
			valueList = cfg.utls.textToValueList(cfg.ui.cloud_mask_classes_lineEdit.text())
			cfg.ui.cloud_mask_classes_lineEdit.setStyleSheet('color : green')
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode())
		except Exception as err:
			cfg.ui.cloud_mask_classes_lineEdit.setStyleSheet('color : red')
			valueList = []
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + (cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
		return valueList
		
		
	# mask band sets
	def maskAction(self):
		self.cloudMaskingBandSet()
		
	# cloud masking
	def cloudMaskingBandSet(self, batch = 'No', bandSetNumber = None, inputClassification = None, outputDirectory = None):
		# class value list
		valueList = self.checkValueList()
		if len(valueList) > 0:
			if bandSetNumber is None:
				bandSet = cfg.ui.band_set_comb_spinBox_9.value()
				bandSetNumber = bandSet - 1
			if bandSetNumber >= len(cfg.bandSetsList):
				cfg.mx.msgWar25(bandSetNumber + 1)
				return 'No'
			if inputClassification is None:
				clssfctnNm = cfg.ui.classification_name_combo_4.currentText()
				clss = cfg.utls.selectLayerbyName(clssfctnNm, 'Yes')
				inputClassification = cfg.utls.layerSource(clss)
			if batch == 'No':
				o = cfg.utls.getExistingDirectory(None , cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Select a directory'))
			else:
				o = outputDirectory
			if len(o) > 0:
				if batch == 'No':
					cfg.uiUtls.addProgressBar()
				bndSetSources = []
				# create list of rasters
				try:
					cfg.bandSetsList[bandSetNumber][0]
				except:
					if batch == 'No':
						cfg.uiUtls.removeProgressBar()
					cfg.mx.msgWar28()
					# logger
					cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' Warning')
					return 'No'
				if cfg.bandSetsList[bandSetNumber][0] == 'Yes':
					ckB = cfg.utls.checkBandSet(bandSetNumber)
				else:
					if batch == 'No':
						cfg.uiUtls.removeProgressBar()
					cfg.mx.msgWar29()
					# logger
					cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' Warning')
					return 'No'
				if cfg.bandSetsList[bandSetNumber][0] == 'Yes':
					ckB = cfg.utls.checkBandSet(bandSetNumber)
					bndSetIf = 'Yes'
				else:
					ckB = cfg.utls.checkImageBandSet(bandSetNumber)
					bndSetIf = 'No'
				if ckB == 'Yes':
					bndSetSources.append(cfg.bndSetLst)
				if len(cfg.bndSetLst) == 0:
					if batch == 'No':
						cfg.uiUtls.removeProgressBar()
					cfg.mx.msgWar28()
					# logger
					cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' Warning')
					return 'No'
				cfg.uiUtls.updateBar(10)
				rCrs = cfg.utls.getCrsGDAL(cfg.bndSetLst[0])
				rEPSG = cfg.osrSCP.SpatialReference()
				rEPSG.ImportFromWkt(rCrs)				
				if rEPSG is None:
					if batch == 'No':
						cfg.uiUtls.removeProgressBar()
					cfg.mx.msgWar28()
					# logger
					cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' Warning')
					return 'No'	
				cfg.uiUtls.updateBar(20)
				cfg.utls.makeDirectory(o)
				eCrs = cfg.utls.getCrsGDAL(inputClassification)
				EPSG = cfg.osrSCP.SpatialReference()
				EPSG.ImportFromWkt(eCrs)
				if EPSG.IsSame(rEPSG) != 1:
					nD = cfg.utls.imageNoDataValue(inputClassification)
					if nD is None:
						nD = cfg.NoDataVal
					#tPMD = cfg.utls.createTempRasterPath('tif')
					#cfg.utls.GDALReprojectRaster(inputClassification, tPMD, 'GTiff', None, 'EPSG:' + str(rEPSG), '-ot Float32 -dstnodata ' + str(nD))	
					tPMD = cfg.utls.createTempRasterPath('vrt')
					cfg.utls.createWarpedVrt(inputClassification, tPMD, str(rCrs))
					cfg.mx.msg9()
					if cfg.osSCP.path.isfile(tPMD):
						inputClassification = tPMD
					else:
						if batch == 'No':
							cfg.uiUtls.removeProgressBar()
						cfg.mx.msgErr60()
						# logger
						cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), " Warning")
						return 'No'
				if cfg.ui.cloud_buffer_checkBox.isChecked() is True:
					size =  cfg.ui.cloud_buffer_spinBox.value()
					struct = cfg.utls.create3x3Window()
					input = inputClassification
					ndM = cfg.utls.imageNoDataValue(input)
					dType = cfg.utls.getRasterDataTypeName(input)
					for s in range(0, size):
						tPMD = cfg.utls.createTempRasterPath('vrt')
						# process calculation
						oP = cfg.utls.multiProcessRaster(rasterPath = input, functionBand = 'No', functionRaster = cfg.utls.rasterDilation, outputRasterList = [tPMD], functionBandArgument = struct, functionVariable = valueList, progressMessage = cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Dilation '), virtualRaster = 'Yes', compress = 'No', outputNoDataValue = ndM, dataType = dType, boundarySize = 3)
						input = tPMD
					if cfg.osSCP.path.isfile(tPMD):
						inputClassification = tPMD
					else:
						if batch == 'No':
							cfg.uiUtls.removeProgressBar()
						cfg.mx.msgErr60()
						# logger
						cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), " Error")
						return 'No'
				# No data value
				NoDataVal = cfg.ui.nodata_spinBox_11.value()
				nD = NoDataVal
				outputName = cfg.ui.mask_output_name_lineEdit.text()
				if len(outputName) > 0:
					outputName = str(outputName.encode('ascii','replace'))[2:-1] + "_" 
				cfg.uiUtls.updateBar(40)
				# create functions
				bList = []
				bandNumberList = []
				bList.append(inputClassification)
				bandNumberList.append(1)	
				outputList = []
				argumentList = []
				variableList = []
				varList = []
				varList.append('"im0"')
				for x in range(1, len(cfg.bndSetLst) + 1):		
					varList.append('"im' + str(x)+ '"')
				for x in range(1, len(cfg.bndSetLst) + 1):			
					if bndSetIf == 'Yes':
						bList.append(cfg.bndSetLst[x-1])
						bandNumberList.append(1)
					else:
						bList.append(cfg.bndSetLst[x])
						bandNumberList.append(x)
					rstrOut = o + '/' + outputName + cfg.utls.fileNameNoExt(cfg.bndSetLst[x-1]) + '.tif'
					outputList.append(rstrOut)
					# function
					e = ''
					end = ''
					for c in valueList:
						e = e + 'cfg.np.where("im0" == ' + str(c) + ', cfg.np.nan, '	
						end = end + ')'
					e = e + '"im' + str(x) + '"' + end
					argumentList.append(e)
					variableList.append(varList)
				# create virtual raster					
				vrtCheck = cfg.utls.createTempVirtualRaster(bList, bandNumberList, 'Yes', 'Yes', 0, 'No', 'Yes')
				# open input with GDAL
				rD = cfg.gdalSCP.Open(vrtCheck, cfg.gdalSCP.GA_ReadOnly)
				# output rasters
				cfg.utls.createRasterFromReference(rD, 1, outputList, cfg.NoDataVal, 'GTiff', cfg.rasterDataType, 0,  None, compress = 'Yes', compressFormat = 'LZW')
				rD = None
				# process
				o = cfg.utls.multiProcessRaster(rasterPath = vrtCheck, functionBand = 'No', functionRaster = cfg.utls.calculateRaster, outputRasterList = outputList, nodataValue = nD, functionBandArgument = argumentList, functionVariable = variableList, progressMessage = cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Mask'), outputNoDataValue = nD, compress = cfg.rasterCompression, compressFormat = 'LZW', parallel = cfg.parallelRaster, skipSingleBand = 'Yes')
				cfg.cnvs.setRenderFlag(False)
				for rOut in outputList:
					if cfg.osSCP.path.isfile(rOut):
						# add raster to layers
						cfg.utls.addRasterLayer(rOut)
				cfg.cnvs.setRenderFlag(True)
				cfg.uiUtls.updateBar(100)
				if batch == 'No':
					cfg.utls.finishSound()
					cfg.utls.sendSMTPMessage(None, str(__name__))
					cfg.uiUtls.removeProgressBar()
				