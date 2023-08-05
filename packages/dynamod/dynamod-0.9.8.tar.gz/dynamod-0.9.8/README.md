Dynamod - a tool for modelling infectious diseases
==================================================

Dynamod is a tool written in Python to build and run compartmental models in epidemiology.

In Dynamod, the model is represented in a [formal model description language](MODEL_REFERENCE.md). This model file is both human-readable and machine-readable. It can be used to explain and discuss the model, while at the same time it is the direct input to the calculation of the model results without any further programming necessary (see the [User Guide](USER_GUIDE.md) for reference).

Dynamod represents compartments as a multi-dimensional combination of attributes (e.g. age, risk group, state of infection, state of vaccination etc.). Initial shares and state transitions along these attribute axes can be modelled as dependent on other attributes.

Transitions can be described in two ways: either by the rate of change at each step of the iteration (leading to a differential equation), or by specifying the distribution of the transition time. This reflects the epidemiological reality better than a purely differential approach. For example, in the SEIR model it is rather sensible that in a well-mixed population the transition S -> E is differential (depending on the shares of S and I), whereas the transitions E -> I and I -> R likely behave differently, maybe following a normal distribution centered around the mean latency and recovery period, respectively. If modelled as differential transitions, a completely different probability distribution of latency and recovery periods would result. That follows, because the holding time in a differential transition (homogeneous Poisson process) follows an exponential distribution.

Iteration steps can be arbitrary amounts of time, this is just an interpretation of the time axis. Differential transitions are described "per tick" and time distributions also correspond to this unit of time.

Dynamod offers the concept of extending models, so more complex models can be built upon existing and proven base models, without changing the base models themselves. Using this approach, multiple models sharing the same basis can be run against each other, for example to study the effects of different alternative interventions.

To enable model extension, Dynamod works with named objects. Any named object defined in an extension model will replace the object with that name in the base model (or added if no such object exists). All core elements of the model (attributes, progressions, parameters, formulas and results) are named objects.

If the standard means of model description are not sufficient (or too cumbersome), Dynamod can be transparently extended by inserting arbitrary Python objects into Dynamod's namespace and invoking functions on these objects.

An automated parameter fitting algorithm finds values for a given set of parameters that (at least locally) minimizes the difference between a set of results and their respective expected outcomes. As target, series of result values can be specified as well as time and/or value of time series maxima and minima. 

The parameter fitting utilizes gradient descent with grid search, integral parameter support and auto-adaptive learning rate. For details see python package "gradescent".
