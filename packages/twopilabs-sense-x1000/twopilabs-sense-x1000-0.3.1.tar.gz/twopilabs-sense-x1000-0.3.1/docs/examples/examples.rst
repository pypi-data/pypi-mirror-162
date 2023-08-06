.. _section-examples:

Examples
========
This section contains a list of examples that focus on various aspects of using your 2πSENSE X1000 series device.
The example scripts shown here are directly runnable by a python system where the required packages (see :ref:`section-introduction`) are installed.

.. toctree::
   :hidden:

   alternating-sweeps
   multi-channel
   live-plot

* :ref:`examples-alternating-sweeps`

  This example shows how the device can be used to perform multiple sweeps by a single trigger event with alternating sweep slopes.
  The generator syntax method is used to receive and process the data in pairs of 2 consecutive sweeps.

* :ref:`examples-multi-channel`

  Depending on the physical configuration, 2πSENSE X1000 series device can support multiple receive channels. 
  This example shows how data can be received from multiple channels by enable additional `traces`.

* :ref:`examples-live-plot` 

  A simple live plotting demo with basic fft processing and axis calculation. 
  Plotting is handled by ``matplotlib`` and sweep parameters can be customized from command-line
