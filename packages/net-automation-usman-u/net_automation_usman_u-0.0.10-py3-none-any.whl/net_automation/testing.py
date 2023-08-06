import net_automation

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
erx_zahid_lan = net_automation.EdgeOS(
    "erx.zahid.lan",
    "usman",
    "",
    True,
    r"c:\Users\Usman\.ssh\id_rsa",
    ""
)
_2960_usman_lan = net_automation.Cisco_IOS(
    "2960.usman.lan",
    "usman",
    "",
    False,
    "",
    ""
)

edge_dn42_lan.init_ssh()
erx_usman_lan.init_ssh()
erx_zahid_lan.init_ssh()
_2960_usman_lan.init_ssh()

edge_dn42_lan_commands = (edge_dn42_lan.set_lldp(["all"], ["cdp"]))
erx_usman_lan_commands = (erx_usman_lan.set_lldp(["all"], ["cdp"]))
erx_zahid_lan_commands = (erx_zahid_lan.set_lldp(["all"], ["cdp"]))
_2960_usman_lan_commands = (_2960_usman_lan.set_lldp(True))

print ("""
Candidate config for edge.dn42.lan: {}
Candidate config for erx.usman.lan: {}
Candidate config for erx.zahid.lan: {}
Candidate config for 2960.usman.lan: {}""".format(edge_dn42_lan_commands,
                                            erx_usman_lan_commands, 
                                            erx_zahid_lan_commands, 
                                            _2960_usman_lan_commands))


confirm = input("Do you want to commit these changes? (y/n) ")
if confirm == "y":
    edge_dn42_lan.config_mode()
    edge_dn42_lan.bulk_commands(edge_dn42_lan_commands)

    erx_usman_lan.config_mode()
    erx_usman_lan.bulk_commands(erx_usman_lan_commands)

    erx_zahid_lan.config_mode()
    erx_zahid_lan.bulk_commands(erx_zahid_lan_commands)

    _2960_usman_lan.bulk_commands(_2960_usman_lan_commands)

verify_commit = input("Do you want to check the command conflicts before comitting? Y//N [Y]") 
if verify_commit == "N":                                 
    erx_usman_lan.commit()
    erx_zahid_lan.commit()
    edge_dn42_lan.commit()
else:                                                        
    print (erx_zahid_lan.get_changed())
    print (erx_usman_lan.get_changed())
    print (edge_dn42_lan.get_changed())


commit = input("Do you want to commit these changes? (y/n) ")
if commit == "y" or commit == "Y":                                 
    erx_usman_lan.commit()
    erx_zahid_lan.commit()
    edge_dn42_lan.commit()
else:
    erx_usman_lan.discard_changes()
    erx_zahid_lan.discard_changes()
    edge_dn42_lan.discard_changes()

save = input("Do you want to save the configuration to disk? Y/N [N]")
if save == "Y" or save == "y":
    print (erx_usman_lan.save_config())
    print (erx_zahid_lan.save_config())
    print (edge_dn42_lan.save_config())
else:
    print ("Config not saved to disk")