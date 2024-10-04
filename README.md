# A Bayesian Framework for Learning Proactive Robot Behaviour in Assistive Tasks

## Abstract
Socially assistive robots represent a promising tool in assistive contexts to improve people’s quality of life and well-being through social and emotional support, just like cognitive or physical. However, the effectiveness of interactions depends significantly on their ability to adapt to the needs of the assisted persons and act proactively in an anticipatory way, offering assistance before it is explicitly requested. Unfortunately, most of the previous work has only focused on what actions the robot should perform, rather than considering when to act and how confident it should be in a given situation. To address this gap, in this paper, we introduce a new data-driven framework that involves the use of a learning pipeline, consisting of 2 phases, with the ultimate goal of training an algorithm based on Influence Diagrams. The assistance scenario involves a sequential memory game where the robot learns autonomously what assistance to provide, when and with what confidence to take control and intervene. The results obtained from a user study showed that the proactive behaviour of the robot had a positive impact on the users’ game performance. They obtained higher scores, made fewer mistakes, and requested less assistance from the robot. The study also highlighted the robot’s ability to provide assistance tailored to users’ specific needs and to anticipate their requests.

![user](./assets/user.png)


## In brief

In order to discover how robots can be endowed with proactive behaviour, we devised a learning pipeline consisting of two main phases.

![pipeline](./assets/pipeline.png)

- Phase 1. [**Learning to be Proactive**](https://github.com/Prisca-Lab/proactive_robot_behaviour/tree/main/learning%20to%20be%20proactive), in which we request participants to play alone with the possibility of asking for assistance when necessary; 
- Phase 2. [**Learning to be Proactive with Confidence**](https://github.com/Prisca-Lab/proactive_robot_behaviour/tree/main/learning%20to%20be%20proactive%20with%20confidence), in which participants play with the assistance of a proactive virtual-screen robot trained with the data collected in the previous phase; 

Finally, we evaluate the learned system with the robot [**Proactive Robot with Confidence**](https://github.com/Prisca-Lab/proactive_robot_behaviour/tree/main/proactive%20robot%20with%20confidence), in which participants play with the Furhat robot endowed with the model fine-tuned in the second phase. 

![influence_diagram](./assets/ID.png)


## Main Findings

- The results showed that participants who interacted with the proactive robot achieved significantly higher scores and made fewer mistakes compared to those interacting with the non-proactive robot.
  
- Importantly, there was no significant difference in the amount of assistance provided between the two conditions, indicating that the proactive robot was more effective at delivering the right assistance at the right time.
  
- The study also found that participants who interacted with the proactive robot requested assistance less often, further supporting the system’s ability to anticipate their needs.
  
- However, there was no significant difference in how participants perceived the two robots in terms of social intelligence and proactivity. 

![overall_results](./assets/overall_results.png)
<p align="center">
  <img src="./assets/assistance_activated.png" alt="assistance_activated" width="400"/>
</p>
