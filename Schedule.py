import spaces
from spaces import Space, Dorm, SubSpace
import CovidAgents

ag = CovidAgents.Agent().initialize()

small_dorm = spaces.Space.__init__(Dorm, "Small")
medium_dorm = spaces.Space.__init__(Dorm, "Medium")
large_dorm = spaces.Space.__init__(Dorm, "Large")

small_dorm2 = spaces.Dorm.__init__("Small")
medium_dorm2 = spaces.Dorm.__init__("Medium")
large_dorm2 = spaces.Dorm.__init__("Large")
