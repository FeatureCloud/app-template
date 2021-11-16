# FeatureCloud Engine
### Defining states and running applications

FeatureCloud provide an advantageous platform to develop Federated applications.
FeatureCloud includes different components to develop applications in a privacy preserving fashion and present 
them to researchers and practitioners. FeatureCloud AI store includes different exciting applications developed from
FeatureCloud community, a testbed to facilitate app development for developers, and project frontend for FeatureCloud
end-users to run desired workflows that can contain multiple applications. For registering and testing your apps
or using other apps, please visit [FeatureCloud.ai](https://featurecloud.ai/). And for more information about
FeatureCloud architecture, please refer to our [The FeatureCloud AI Store for Federated Learning in Biomedicine and Beyond](https://arxiv.org/abs/2105.05734) [[1]](#1).


FeatureCloud library provides app developers with  `AppState` and`App` classes, that are useful 
to define states and execute app instances, respectively. Each app, in FeatureCloud platform, includes multiple states,
and possible transitions between the defined states. All apps will begin their workflow from `initial` state
and end it at `Finish` state. Accordingly, `App` class will manage registering user defined states in the app workflow
and also, registering transitions. FeatureCloud `App` supports exactly two roles, coordinator and participant, for clients who are going to participate
in Federated execution of apps. FeatureCloud app-developers are obliged to explicitly define their logic
for the app, by stipulating which roles are allowed to enter a specific state and take a particular transition( we will elaborate on this part later).

## Roles
In FeatureCloud platform, clients can have two roles: coordinator and participant.These roles are not mutually-exclusive.
Meanwhile, FeatureCloud library, comes with three important constant tuples to describe eligibility of 
clients in terms of their role, to enter and execute specific states.  Accordingly, to make it clear, we defined three role tuples, with `bool` values, 
for participant and coordinator roles, as follows: 

* `COORDINATOR`: indicates that only coordinator role is `True` 
* `PARTICIPANT`: indicates that only participant role is `True`
* `BOTH`: indicates that both roles are `True`

To avoid Confusion, FeatureCloud app-developers can use these constants for defining roles for states and transitions . 

##  Operational States
Once states are executing, any exceptions or errors can happen that can be handled automatically by the app.
For reporting the situation for front-end app, so end-users be aware of it, currently, there are three key values
that can be communicated to the controller:

Operational states | 'running' | 'error' | 'action_required' 
--- | --- | --- | --- |
Constants | RUNNING | ERROR | ACTION | 
 
FeatureCloud app-developers can use this pre-defined values for updating the front-end for end-users.
To avoid typos, developers can use the constants.  

## Secure Multi-Party Computation (SMPC)
Despite privacy-awareness in Federated Learning, not sending around raw data, still there are a couple of steps
to strengthen privacy issues. In that regard, FeatureCloud provides Secure Multi-Party Computation (SMPC) 
module for aggregating clients data. In SMPC component, you can include all or at least two of clients as Computational
Parties (CP). Those parties will receive exclusively either of noisy data or noises from clients. The amount of noise that
should be used to make data noisy is can be tricky. In one side excessive noise can
damage the results, and on the other hand, slim noises can compromise the privacy. Practically, noise value
should be selected regarding the data range. After getting noisy data and/or noises, each Computation
party sums up the data and move the results to the coordinator. Finally, the coordinator will conclude the aggregation phase.
SMPC component is part of FeatureCloud Controller, however, App-developers could have a basic understanding of its application
to provide the controller with proper SMPC configuration. For more information about the SMPc module, please visit [FeatureCloud.ai](https://featurecloud.ai/)
or refer to our [paper](https://arxiv.org/abs/2105.05734) [[1]](#1).

### Exponent
To make the data noisy, a noise value should be drawn randomly. Regarding the fact that noise values cannot
be zero or negative. Exponent should be a non-negative integer where zero practically means not using SMPC component.

### Shards
Each client should send out noise and noisy data to Computational parties, which can be at least two and at most,
the number of clients. Noise can be made of one or more secrete values, and clients should generate those secrete random values 
regarding the number of shards. For instance, once the shards are two, clients should send out one secrete value, 
and noisy data, of coarse, to different CPs. For three or more shards, more secrete values should be generated.
Even though maximum number of parties yields the best privacy preserving results, 
it is computationally expensive. Accordingly, `shards` is a non-negative integer, where choices are:
- `0`: Maximum number of computational parties(Number of clients)
- `1`: Practically, SMPS module will not be use in an effective way.
- `Values grater than one`: indicates number of Computational parties that will be involved.
 
### Operations
For employing noise to the clients' data, we can use different operation. Currently, FeatureCloud supports 
two of the most common operations to make noisy data: add and multiply. App-developers can choose between 
these two options by providing the string value of `add` or `multiply`, or simply to avoid typos, they can 
use following constants:
```
OPERATION_ADD = 'add'
OPERATION_MULTIPLY = 'multiply'
```

### Serialization
To communicate the aggregated results of SMPC module to the coordinator, the results should be serialized.
For serialization technique, FeatureCloud library, currently, supports `json` serialization.
For using it, developers, can pass exact string value of `json` to the controller.  


## App class
`App` is the main part of FeatureCloud library, which enables users to register their states and transitions.
In an OO fashion, just by extending `AppState`, developers can use FeatureCloud library for
implementing one-shot or iterative applications. 
This template consists of three main classes to interact with FC Controller and execute the app-level tasks. Generally, two types of clients are used in FeatureCloud Template:

- participant: Every participant in the FeatureCloud platform, except for one, the coordinator,
  are considered as participants who should perform local tasks and communicate some intermediary results with the coordinator.
  Of course, no raw data are supposed to be exchanged among clients and the coordinator.
- coordinator: One of the clients who can receive results of other clients, aggregate, and broadcast them.



For registering either states or transitions, app-developers are required to use one of these constants
to declare that each role/s are responsible/allowed to execute states or take transitions. `App` class
automatically checks the logic to ensure semantic errors in defining the workflow are minimized.

#### `_register_state`
It instantiates a state and add it as part of the app workflow. It gets following parameters: 
+ name: name of the state(which will be used in logging and creating transitions)
+ state: AppState class or any extensions of it.
+ participant: boolean flag that indicates whether participants are allowed to enter the state or not.  
+ coordinator: boolean flag that indicates whether the coordinator are allowed to enter the state or not.

#### `register_transition`
It has similar application as `_register_state` except it registers states. It recives names of source and 
target states, and register it.Meanwhile, it checks the logic and raises `RuntimeError` if apps try to register a
transitions with contradicting roles.


#### Transition to another state: `transition`
Transits the app workflow to the unique next state based on current states, the role FeatureCloud client,
and requirements of registered transitions for current state.`

#### Registering all transitions: `register`
It will be called once the app is contact with the FeatureCloud Controller to register all the user-defined 
states.

#### Registering state transition: `register_transition`
Adds new transition to the group of possible transitions in the workflow, while ensures that the logic of states
and transition holds by checking allowed roles to transit from a source state to a target state.

#### Executing state's computation: `run`
It is the main method in `App` class that runs the workflow, while logs the current state when executes it,
and transits to the next desired state. Meanwhile, once the app transits to the finish state,
the workflow will be terminated.

## AppState: Defining Custom States
To Support all sorts of operations and communications FeatureCloud's engine package includes `AppState` 
class. It is an abstract class that requires App-developers to extend it by defining its abstract methods:
`register()` and `run()`. In `AppState.register` method users should call `register_transition` of the state
for adding possible transitions. Sates are assigned to clients with specific roles, and FeatureCloud app 
will verify all states and their corresponding transitions based on these predefined roles. In this way, 
logic of app can be verified before deploying it(More on this on FeatureCloud's Utils package). Each state
should have a unique name that by default will be used for naming transitions. Also, for roles, developers
should set `participant` and `coordinator` attributes(which we strongly recommend to use [`app_state`](#registering-states-to-the-app-app_state) handler).  
Also for each state, the app instance should be assigned, so states can have access to app's attributes,
especially `internal` attribute that should be used as a shared memory between all states.

`AppState` includes generic methods for sending data around that all use json serialization regarding SMPC usage. 
To provide more secure way of communicating data, FeatureCloud incorporates Secure Multu-Party Computation (SMPC), 
and regarding using it or not, different serialization methods will be used:

- `json`: will be used once we do not use SMPC for aggregation and can handle Numpy arrays and Panda DataFrames and Series.
- `pickle`: will be used once SMPC is used for aggregation and only supports Python lists, tuple, and dictionaries.

Therefore, app-developers should consider data type and structure when they communicate data that should be aggregated.
The data may not be in the same structure or type as they sent out.

#### Registering a specific transition for state: `register_transition`
Developers should call this method to register a transition for the state by determining the name of
`target` state, `role` tuple of transitions, and a post-fix name for generate the name of the transition.
In case of not providing the postfix, name of the target state will be used. For naming the transitions,
we conventionally use `name of source state`_`name of target state`.

#### Aggregating clients data: `aggregate_data` 
This method automatically handles SMPC usage and serialization and always returns the aggregated data. Aggregated data 
contains same data structure and shape as the one was sent out by each of clients, it sums up data elements. Therefore,
to have structural data consistency, it considers SMPC usage as follows:
- Using SMPC: waits to recieve the aggregated data from SMPC modules, it looks like waiting for just one client.
- Without SMPC: waits to recieve all clients data, then internally aggregates them.

Accordingly, FeatureCloud app-developers no longer are required to consider SMPC usage, because they always get the same
aggregated results in the coordinator. Provided aggregated results, are not the average ones, therefore they need to be 
averaged, if it's apt to, separately.

#### Gathering clients data: `gather_data`
FC app-developers are allowed to call this method only for clients with the coordinator role.
This method calls `await_data` method to wait for receiving data of all clients.            

#### Waiting to receive data: `await_data`
For receiving data from `n` clients, it can be called. It polls for data arrival every `DATA_POLL_INTERVAL` seconds, 
and once its received, deserializes the received data.  

#### Communicating Data to others: `send_data_to_participant`
Once it is called, it communicates data to another specific client that was named by its `id`.

#### Configuring SMPC Module `configure_smpc`
 Developers can configure the Secure Multi-Party Computation(SMPC) module by sending range, shards,
 operation, and serialization parameters. In case of not calling the method, default configurations will be used
 (More information on [here](#secure-multi-party-computation-smpc)).

#### Communicating data to the coordinator: `send_data_to_coordinator`
To Communicate data with coordinator, FC app-developers can use this method. 
It provides data for the FC Controller to deliver the data. And if it is called by the coordinator,
data will be directly appended to its list of incoming data. Developers should decide whether they want
to employ SMPC for securing the aggregation or not by setting `use_smpc` flag.

#### Broadcasting data: `broadcast_data`
This should be only called for the coordinator to broadcasts data to all clients.

#### Updating local app status: `update`
Updates the status of the instance app for front-end application. it can be called by any of clients to report client's state.
- message: messaging any specifics about state or app. 
- progress: quantifies the approximate progress of the application. 
- state: message that describes actual/general state of the app.





## Registering states to the app: `app_state`
Once FC app-developers want to integrate their newly defined states into the app, they can use `app_state`. FeatureCloud app
will always be instantiated in `FeatureCloud.engine` package to be used by different modules. Each state should be 
defined for at least one of participant or coordinator roles. In case states require any specific arguments, it should be 
sent by the `app_state` function.
For instance, to register the `initial` state with the constant role of `BOTH` and `app_name` as a state specific argument,
we can use `app_state` as follows:

```angular2html
@app_state(name='initial', role=BOTH, app_name=name)
class ExampleState(State):
    def __init__(app_name)
```
This will automatically register `ExampleState` as the first state, by the name of `initial` in the app. Meanwhile, once the
state is instantiated, `app_name` will be passed to it.

## ConfigState
### Automatic Handling of config files, I/O paths, and splits
FeatureCloud Engine provides FeatureCloud app-developers with basic `AppState` class to define custom states. `AppState`
leaves most of the operations that could be similarly handled in different states to developers. It supports maximum flexibility
with imposing minimum restrictions. Here we introduce Custom states as abstract classes that provides developers with 
plenty of helper functions to deal with various operations transparently. For instance, in `Appstate` there are no path for 
input data, and developers should handle finding them in `/mnt/input` directory inside the docker container. But in our custom
stated, we will transparently make them available for developers, which entail them to follow specific conventions and formats
to develop their apps.

## ConfigState
Many of FeatureCloud apps expect to have Input files, `config.yml` file, and output files. All input files
should be copied into the same directory inside the docker container to be accessed by the app. To facilitate the I/O process 
`ConfigState` define methods to automatically find the paths to all input and output files with considering the logic(data splits).
Accordingly, it stores values in app internal dictionary for  `smpc_used`, `splits`', `input_files`, and `output_files`.
It is meant to use `ConfigState` for defining just one state, the `initial` one, first one, to set up all the required values 
for all following states in the app. `ConfigState` should be used in an app that all other states are defined based on `GeneralState`
because it provides paths and splits that are required in other states to process the data.

#### def lazy_init()
After defining the state, for adding new kew-value pairs into the app internal, this method should be called inside run method
of the extended state. it ensures that these key-values inside app internal exist and have the right value:
- `smpc_used`: It's a flag to remember either SMPC was used previously or not. It will be handled internally by the `GneralState`
methods.
- `splits`: names of different split for each data part which can be used to keep the order of processing them.
- `input_files`: paths to of different input data with considering number of splits.  
- `output_files`: paths to of different output data with considering number of splits.

#### read_config()
Read config.yml file it looks for `mode` and `dir` in `logic` part of the file, 
if dose not exist, default values will be used

#### finalize_config()
Generates split names, paths to input and output files. Regarding the `mode` of the app, there should be some splits for data
and for each data, different splits should be processed
        


### References
<a id="1">[1]</a> 
Matschinske, J., Späth, J., Nasirigerdeh, R., Torkzadehmahani, R., Hartebrodt, A., Orbán, B., Fejér, S., Zolotareva, O., Bakhtiari, M., Bihari, B. and Bloice, M., 2021. The FeatureCloud AI Store for Federated Learning in Biomedicine and Beyond. arXiv preprint arXiv:2105.05734.
