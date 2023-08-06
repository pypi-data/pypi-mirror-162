# Buehltech Home Automation

### Overview

This project implements a system that enables sensing and control of various devices in a home.

Any device in the home that can be sensed or controlled electronically can be connected to a system that can manage that device and allow remote access. Examples of devices include such things as light fixtures, sprinkler valves, temperature sensors, door sensors, etc.  This project does not define specific hardware for these devices, but rather defines the software that allows any device to be interfaced to the system.

At the lowest level, a template is defined that allows a hardware interface to be abstracted to a common API.  The server on which the software is running may physically connect to the device using any hardware interface such as GPIO pins, a serial port, or a network adapter.  An object model is defined that is implemented with an application running on that server that further abstracts the specific functions of the device.  Network protocols are defined that enable the server to advertise itself on the network and allow access to the devices that it is connected to. Other servers may implement human interfaces such as a web server.

### Terminology

First, let's define the terminology used in this project.

##### HARDWARE
These describe the physical hardware that the system is built from.

- device - the hardware components that make up the system
- sensor - a device that has a state that can be read
- control - a device whose state can be read and also changed
- server - a device that may be connected to one or more sensors and communicates with one or more clients
- client - a device that communicates with one or more servers
- interface - the connection over which two devices communicate

##### OBJECT MODEL
These are the core Python classes that are used to describe the system.

- Object - the base class for everything
- Resource - base class for resources
- Sensor - a resource that is a representation of a physical sensor
- Control - a resource that is a representation of a physical control
- Interface - a resource that is a representation of a physical interface
- Collection - a resource that is an ordered list of resources

##### IMPLEMENTATION
These terms describe the roles played by the software components in the system.

- application - the implementation of a collection of resources and interfaces that runs on a server
- service - an application that implements the server side of an interface to a client device or server device
- client - an application that implements the client side of an interface to a server device

### Example

A simple example is a temperature sensor that may be in a room, outside the house, or immersed in a swimming pool.  All it does is to report the ambient temperature of the air or water it is in.  Let's consider a digital temperature sensor that uses the I<sup>2</sup>C hardware interface.  When a read command is sent to the address of the device it returns a byte that represents the temperature in degrees Celsius.  Two software objects defined by this project are required: a Sensor and an Interface.  The Sensor can be just the base object because all it needs to do is to implement the get state function that reads the state of the sensor from the interface it is associated with.  The Interface object must be specific to the I<sup>2</sup>C interface so it is a I2CInterface object that is derived from the base Interface object.  It can use the Python SMBus library that performs all the low level I<sup>2</sup>C protocol functions to read a byte and implement the read function.

Another example is a sprinkler valve.  The state of the valve is either open or closed, and it is operated remotely from the network.  The voltage to the valve is switched using a relay or semiconductor that is controlled by a GPIO pin on the controller.  A Control object and an Interface object are needed to implement this.  The Control object inherits the get state function from the Sensor object, but it also defines a set state function that changes the state of the device.  The GPIOInterface object implements the read and write functions that get and set a GPIO pin.

### Design goals

The design of the project targets the following goals.  Not all of them have been strictly met.

-  Distributed - Functions are distributed across devices in the system.
-  Devices are autonomous - Whenever possible, devices can run independently of the system.  There is no requirement for a centralized controller.
-  Devices are dynamically discoverable - Devices can be added or removed from the system without requiring changes to a system configuration.
-  Connected to the local home network - Devices are connected to the system via the local wired or wireless home network.
-  Not dependent on the internet for critical functions - The system may be accessed remotely via the internet and use cloud servers for certain functions, however internet connectivity is not required.
-  Reasonably secure - The system does not explicitly implement any security features.  It relies on the security of the local network.
-  Not dependent on proprietary systems, interfaces, or devices - Proprietary interfaces and devices may be accessed, but there is no requirement for any particular manufacturer's products.
-  Not operating system specific - There is no dependence on any operating system specific features.
-  Open source - All code is open source.

### Naming

Every resource has a system-wide unique identifier.  The namespace is flat.

### States

Every Sensor has an associated state.  A Sensor state is a single scalar number or string.  If a device has multiple attributes or controls, it should be represented as multiple Sensor or Control objects.  The state of a Sensor is obtained by an explicit call.  A Sensor may implement an event that is set when its state changes that can be used for notification.

### Object model

The object model is defined by the following core classes:

	+ class Object(object):
		+ class Resource(Object):
		    - class Interface(Resource):
		    + class Sensor(Resource):
		        - class Control(Sensor):
		    + class Collection(Resource, OrderedDict):

##### Object
The base class for HA objects.  It implements the dump() function which is used to serialize objects as JSON.  Deserialization is implemented by the static loadResource() function.

	- dump()

##### Resource
The base class for all HA resources.

    - name
	- type
	- enable()
	- disable()

##### Interface
Defines the abstract class for interface implementations.

    - interface
    - sensors
    - event
    - start()
    - stop()
    - read(addr)
    - write(addr, value)
    - notify()

##### Sensor
Defines the model for the base HA sensor.

    - interface
    - addr
    - event
    - label
    - group
    - location
    - notify()
    - getState()

##### Control
Defines the model for a sensor whose state can be changed.

    - setState(value)

##### Collection
Defines an ordered collection of Resources.

	- addRes()
	- delRes()
	- getRes()

Other generally useful classes are inherited from the core classes:

	+ class SensorGroup(Sensor):
		- class ControlGroup(SensorGroup, Control):
		- class SensorGroupControl(SensorGroup, Control):
	- class CalcSensor(Sensor):
	- class DependentControl(Control):
	- class MomentaryControl(Control):
	- class MultiControl(Control):
	- class MinMaxControl(Control):
	- class MinSensor(Sensor):
	- class MaxSensor(Sensor):
	- class AccumSensor(Sensor):
	- class AttributeSensor(Sensor):
	+ class ProxySensor(Sensor):
	 	- class ProxyControl(ProxySensor):

These classes are inherited from the core classes and implement time based functions:

	- class Schedule(Collection):
    - class Cycle(Object):
	- class Sequence(Control):
	- class Task(Control):
    - class SchedTime(Object):

### Sample application

The following sample application illustrates how a service may be implemented.  A temperature sensor and a sprinkler valve are configured as described in the earlier example.

First, the I<sup>2</sup>C and GPIO Interface objects are defined.  The address of the temperature sensor is 0x4b on the I<sup>2</sup>C bus and the sprinkler valve is connected to GPIO pin 17 which is set to output mode.  Then the Sensor object for the temperature sensor and the Control object for the sprinkler valve are defined.  Next, a Task is defined that will run the sprinkler every day at 6PM (18:00) for 10 minutes (600 seconds) every day during the months May through October.

Finally, the task is added to a Schedule object and the Sensor and Control are added to a Collection object that will be exported by the REST server.  When the Schedule is started it will turn on the sprinkler every day as programmed.  The REST server will export the representations of the two resources and their current states.  It will also allow another server to control the sprinkler valve remotely. It must be started last because it will block the application so it will not exit.

```
from ha import *
from ha.interfaces.I2CInterface import *
from ha.interfaces.gpioInterface import *
from ha.rest.restServer import *

if __name__ == "__main__":
	# Interfaces
	i2cInterface = I2CInterface("i2cInterface")
	gpioInterface = GPIOInterface("gpioInterface", output=[17])

	# Temp sensor and sprinkler control
	gardenTemp = Sensor("gardenTemp", i2cInterface, 0x4b, label="Garden temperature")
	gardenSprinkler = Control("gardenSprinkler", gpioInterface, 17, label="Garden sprinkler")

	# Sprinkler task
	gardenTask = Task("gardenTask", SchedTime(hour=18, minute=00, month=[May, Jun, Jul, Aug, Sep, Oct]),
	                    sequence=Sequence("gardenSequence",
								cycleList=[Cycle(control=gardenSprinkler, duration=600, startState=1)]),
								controlState=1,
						label="Garden sprinkler task")

	# Resources and schedule
	schedule = Schedule("schedule", tasks=[gardenTask])
	restServer = RestServer("garden", Collection("resources",
				resources=[gardenTemp, gardenSprinkler]), label="Garden")

	# Start things up
	schedule.start()
	restServer.start()
```
### Implementation

#### Directory structure
```
root directory/
	*App.py - Applications that run on servers
	ha/
		core.py - The core object model
		extra.py - Additional useful objects derived from the core objects
		environment.py - Environment variables
		config.py - Read runtime parameters from the configuration file
		logging.py - Logging functions
		debugging.py - Debugging functions
		schedule.py - Schedule and time based objects
		interfaces/
			*Interface.py - Interfaces to specific hardware
		rest/
			restConfig.py - REST interface parameters
			restServer.py - REST server used by a service
			restProxy.py - REST proxy used by a client
			restServiceProxy.py - The proxy for a REST service used by a client
			restInterface.py - The interface used by resources that are being proxied in a client
		ui/
			webUi.py - A human interface that aggregates all the servers and provides a web interface
			webViews.py
	templates/
		HTML templates
	static/
		css/
		json/
		images/
	services/
		*App.service - The systemd service definitions
```
