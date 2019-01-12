#This is a Nipype generator. Warning, here be dragons.
#!/usr/bin/env python

import sys
import nipype
import nipype.pipeline as pe

import nipype.interfaces.fsl as fsl
import nipype.interfaces.io as io

#Wraps command **bet**
my_fsl_BET = pe.Node(interface = fsl.BET(), name='my_fsl_BET', iterfield = [''])

#Generic datagrabber module that wraps around glob in an
my_io_S3DataGrabber = pe.Node(io.S3DataGrabber(outfields=["out_file, func"]), name = 'my_io_S3DataGrabber')

#Generic datasink module to store structured outputs
my_io_DataSink = pe.Node(interface = io.DataSink(), name='my_io_DataSink', iterfield = [''])

#Wraps command **epi_reg**
my_fsl_EpiReg = pe.Node(interface = fsl.EpiReg(), name='my_fsl_EpiReg', iterfield = [''])

#Create a workflow to connect all those nodes
analysisflow = nipype.Workflow('MyWorkflow')
analysisflow.connect(my_io_S3DataGrabber, "out_file", my_fsl_BET, "in_file")
analysisflow.connect(my_fsl_BET, "out_file", my_fsl_EpiReg, "t1_brain")
analysisflow.connect(my_io_S3DataGrabber, "out_file", my_fsl_EpiReg, "t1_head")
analysisflow.connect(my_io_S3DataGrabber, "func", my_fsl_EpiReg, "epi")
analysisflow.connect(my_fsl_EpiReg, "out_file", my_io_DataSink, "registered_epi")
analysisflow.connect(my_fsl_EpiReg, "epi2str_mat", my_io_DataSink, "epi_to_struc")
analysisflow.connect(my_fsl_EpiReg, "epi2str_inv", my_io_DataSink, "struc_to_epi")
analysisflow.connect(my_fsl_EpiReg, "fullwarp", my_io_DataSink, "epireg_fullwarp")

#Run the workflow
plugin = 'MultiProc' #adjust your desired plugin here
plugin_args = {'n_procs': 1} #adjust to your number of cores
analysisflow.write_graph(graph2use='flat', format='png', simple_form=False)
analysisflow.run(plugin=plugin, plugin_args=plugin_args)
