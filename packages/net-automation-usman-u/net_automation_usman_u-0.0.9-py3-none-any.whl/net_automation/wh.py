import net_automation

rtr = net_automation.Vyos(
    "edge.dn42.lan",
    "usman",
    "",
    True,
    r"c:\Users\Usman\.ssh\id_rsa",
    ""
)

rtr.init_ssh()
server = net_automation.Webhook("https://discord.com/api/webhooks/999979792445222983/tzEfLe66n923yvb4eW-jiHEYnM4jsPrgQRxZSkRw0Qha3ziIrWRpXV6ZKCvJFDMVkiTE")

cf = rtr.get_ping_data("cloudflare.com", 5)
google = rtr.get_ping_data("google.com", 5)
erx_usman_lan = rtr.get_ping_data("10.100.100.1", 5)
erx_zahid_lan = rtr.get_ping_data("10.100.100.2", 5)

results = [cf, google, erx_zahid_lan, erx_usman_lan]

for i in results:
    template = ("""
    ----------------------------
    Ping to:     | {}                  
    From:        | {}
    Packet Loss: | {}%              
    Min RTT:     | {}ms        
    Avg RTT:     | {}ms                
    Max RTT:     | {}ms                                      
    Std Dev:     | {}                  
    ----------------------------
    """.format(i[0], i[6], i[1], i[2], i[3], i[4], i[5]))
    print (template)
    server.send(template)