<html>
    <head>
        <title>Rekap leads Report</title>
        <style type="text/css">
            body {
                margin: 0px;
                padding: 0px;
                text-align: justify;
            }
            #idiv1 {
                border-left: 1mm solid white;
                border-right: 1mm solid white;
                /* border-bottom: 1mm double black; */
                width: 190mm;
                /* min-height: 277mm; */
                margin-left: 10mm;
                margin-right: 10mm;
                padding-top: 5mm;
                /* margin: 10mm; */
                font-size: 11px;
                font-family: arial, helvetica, sans-serif;
            }
            .boldest {
                font-weight: 900;
            }
            .times {
                font-family: 'times new roman', times, sans;
            }
            .mono {
                font-family: 'lucida console', courier, monospace, monotype;
            }
            #idiv6 {
                /* padding: 2mm; */
            }
            /* #idiv6 ol {
                padding: 0px;
                margin: 0px;
            } */
            #idiv6 table {
                width: 100%;
            }
            #idiv6 * {
                font-size: 12px;
                text-align: justify;
                vertical-align: top;
            }
        </style>
    </head>
    <body>
    	<% a = "" %>
    	<% d = "" %>
    	<% ap = [] %>
       % for order in objects:
       		<% a = order.partner_id.user_id.name %> 
       		<% d = order.date_order %>
       		<% ap.append(d) %> 
       					
       % endfor
       PT ASIA CARTON LESTARI </br>
       Rekap Sale </br>
       Periode : ${min(ap)} s.d ${max(ap)} </br> 
       Sales   : ${a} </br></br>
       	 <table border= "1" width="1100px">
       	 <tr><th>Date</th><th>No Order</th>
       	 <th>Customer Code</th><th>Customer Name</th>
       	 <th>No Skp</th><th>status</th><th>Total</th><th>Sales Person</th></tr>
       	 	<% varsm = 0 %>
       	 % for order in objects:
       	  
       	 	<tr>
       	 	<td>${order.date_order}</td><td>${order.name}</td><td>${order.client_order_ref}</td>
       	 	<td>${order.partner_id.name}</td><td>${order.po_sl or ''}</td>
       	 	<td>
       	 	<%
       	 		defchar = ""
       	 		if order.state == "draft":
       	 			defchar = "quotation"
       	 		elif order.state == "manual":
       	 			defchar =  "sale order"	
       	 	%>
       	 	${defchar}
       	 	</td>
       	 	<td>${order.amount_total}</td><td>${order.partner_id.user_id.name}</td>
       	 	</tr>
       	 	<% varsm += order.amount_total %>
       	 % endfor
       	 <tr>
       	 	<td></td><td></td><td></td>
       	 	<td></td><td></td>
       	 	<td>
       	 	</td>
       	 	<td>${varsm}</td><td></td>
       	 </tr>
       	 </table>
    </body>
</html>
