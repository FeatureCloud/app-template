# FeatureCloud App Template

For registering and testing your apps or using other apps, please visit
[FeatureCloud.ai](https://featurecloud.ai/). And for more information about FeatureCloud architecture,
please refer to 
[The FeatureCloud AI Store for Federated Learning in Biomedicine and Beyond](https://arxiv.org/abs/2105.05734) [[1]](#1).


## Developing Apps using FeatureCloud library
FeatureCloud library facilitates app development inside FeatureCloud platform. To develop apps, developers
should define their states and register them to the default app.

### defining new states
for defining new states there are two options with different levels of flexibility and restrictions.
- `FeatureCloud.engin.app.AppSate`: it's a basic state that enables states to communicate with other clients and coordinator.
- `FeatureCloud.CustomSates`: it's a more customized package that includes states which can transparently handle I/O and
data serialization regarding the usage of SMPC module and/or mutiple splits for each data.

#### AppState
`AppSate` is the building block of FeatureCloud apps that covers all the scenarios with verifying mechanism. Each state of 
the app should extend `AppSate`, which as an abstract class with two specific abstract methods:
- register: that should be implemented by apps to register possible transitions between the current state to other states.
This method is part of verifying mechanism in FeatureCloud apps that ensures logically eligible roles can participate in current state
and transition to other ones.
- run: This method is the main part of the state, that executes all operations and calls for communication between FeatureCloud clients.
`run` is another part of verification mechanism in FeatureCloud library, that ensures transition to other states are logically correct
by returning the name of the next state.


#### ConfigSate
`ConfigSate` is part of CustomState package that should be used as the first state, `initial` state, in the app.
It should be used as part of an app that uses GeneralState for defining its states. It provides necessary information
for following states to facilitate data I/O and serialization. 

### Registering apps
For each state, developers should extend one of the abstract states and call the helper function to automatically register
the state in the default FeatureCloud app:

```angular2html
@app_state(name='initial', role=Role.BOTH, app_name='example')
class ExampleState(ConfigState.State):
    def register(self):
        self.register_transition('terminal', Role.BOTH)

    def run(self):
        self.read_config()
        self.app.log(self.config)
        return 'terminal'
```

### building the app
 


### References
<a id="1">[1]</a> 
Matschinske, J., Späth, J., Nasirigerdeh, R., Torkzadehmahani, R., Hartebrodt, A., Orbán, B., Fejér, S., Zolotareva,
O., Bakhtiari, M., Bihari, B. and Bloice, M., 2021.
The FeatureCloud AI Store for Federated Learning in Biomedicine and Beyond. arXiv preprint arXiv:2105.05734.