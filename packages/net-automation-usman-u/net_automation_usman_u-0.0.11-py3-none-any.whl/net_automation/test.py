import net_automation
import textfsm
import matplotlib.pyplot as plt


edge_dn42_lan = net_automation.Vyos(
    "edge.dn42.lan",
    "usman",
    "",
    True,
    r"c:\Users\Usman\.ssh\id_rsa",
    ""
)

erx_usman_lan = net_automation.EdgeOS(
    "erx.usman.lan",
    "usman",
    "",
    True,
    r"c:\Users\Usman\.ssh\id_rsa",
    ""
)

# erx_zahid_lan = net_automation.EdgeOS(
#     "erx.zahid.lan",
#     "usman",
#     "",
#     True,
#     r"c:\Users\Usman\.ssh\id_rsa",
#     ""
# )

# _2960_usman_lan = net_automation.Cisco_IOS(
#     "2960.usman.lan",
#     "usman",
#     "",
#     False,
#     r"c:\Users\Usman\.ssh\id_rsa",
#     "")

vyos = [edge_dn42_lan]
# edge_os = [erx_usman_lan]
# cisco = [_2960_usman_lan]

# for i in vyos:
#     i.init_ssh()

#     ints = i.get_interfaces()

#     for j in ints:
#         print (j)

# for i in cisco:
#     i.init_ssh()

#     ints = i.get_interfaces()
    
#     for i in ints:
        # print (i)

# with open ("template.textfsm", "r") as template:
#     re_table = textfsm.TextFSM(template)

#     for i in edge_os:

#         i.init_ssh()
#         raw_ints = i.get_interfaces()

#         # ints = """{}""".format(raw_ints)
#         # print (ints)

#         data = re_table.ParseText(raw_ints)



#         for j in data:
#             print (j)

edge_dn42_lan.init_ssh()
ping_data = net_automation.Main.get_ping_data(edge_dn42_lan, "fast.com", 5)
net_automation.Main.gen_ping_graph(ping_data)