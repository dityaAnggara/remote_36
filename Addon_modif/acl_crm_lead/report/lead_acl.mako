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
       % for leads in objects:
       		<% a = leads.user_id.name %> 
       		<% d = leads.visit_date %>
       		<%   f = d.split(" ") %>
       		<%   fdate = f[0].split("-") %>   
       		<% ap.append(f[0]) %> 
       					
       % endfor
       
       Report Kunjungan Sales </br>
       Periode : ${min(ap)} s.d ${max(ap)} </br> 
       Sales   : ${a} </br></br>
       	 <table width="1100px">
       	 <tr><th>Company</th><th>Tanggal</th>
       	 <th>Jam</th><th>Contact Person</th>
       	 <th>Subjet</th><th>Internal Notes</th><th>Sales</th></tr>
       	 % for leads in objects:
       	 	<tr>
       	 		<td>${leads.partner_name}</td>
       	 		<% dx = leads.visit_date %>
       	 		<%   l = dx.split(" ") %>
       	 		<td>${l[0]}</td>
       	 		<td>${l[1]}</td>
       	 		<td>${leads.contact_name}</td>
       	 		<td>${leads.name}</td>
       	 		<td>${leads.description or ' - '}</td>
       	 		<td>${leads.user_id.name}</td>
       	 	</tr>			
       	 % endfor
       	 </table>
    </body>
</html>
