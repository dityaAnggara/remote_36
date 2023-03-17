<html>
    <head>
        <title>OutStanding SKPReport</title>
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
    	<% orgnnmm = "" %>
    	
       % for order in get_ord():
       		<% d = order.create_date %>
       		<%   f = d.split(" ") %>
       		<%   fdate = f[0].split("-") %>   
       		<% ap.append(f[0]) %> 
       		<% orgnnmm = order.name %>			
       % endfor
        
       Report OutStanding SKP </br>
       Periode : ${min(ap)} s.d ${max(ap)} </br> 
        <table width="1100px">
       	 <tr><th>Date</th><th>No SKP</th>
       	 <th>Customer Code</th><th>Customer Name</th> 
       	 <th>Status</th><th>Total Qty</th><th>Total Delivery</th><th>Sisa Delivery</th></tr>
       	 
       	 % for order in get_ord():
       	   <% tot_qty = 0 %>
       	 <% tot_del = 0 %>
       	    % for mo_s in get_records(order.name):
       	    	<% df = brw_movv(mo_s) %>
       	 		<% tot_del += df.product_qty %>
       	     % endfor
       	 	% for line in order.order_line:
       	 	<%	tot_qty += line.product_uom_qty %>
       	 	% endfor
       	   <% stto = "" %> 
       	    % if order.partner_id.active == True: 
		      <% stto = "active" %> 
		    % else: 
		      <% stto = "inactive" %> 
		    % endif
		    		         		 		
       	 	<% siss_dl = tot_qty - tot_del %>
       	 	<tr><td>${ order.create_date or '' }</td><td>${ order.po_sl or '' }</td><td>${ order.partner_id.ref or ''}</td><td>${ order.partner_id.name or '' }</td>
       	 	<td>${ stto or '' }</td><td>${ tot_qty or 0 }</td><td>${ tot_del or 0 }</td><td>${ siss_dl or 0 }</td></tr>
       	 	
       	 	<tr><th></th><th>No KIP</th><th>Product</th><th>Qty</th><th>Total Delivery</th><th>Sisa Delivery</th>
       	    <th></th><th></th></tr>
       	   % for linc in order.order_line:
       	 	  
       	 	  <% too_dl = 0 %>	
       	 		% for dfg in rcrd_toe(order.name, linc.id):
       	 			<% line_f = brw_movv(dfg) %>
       	 			<% too_dl += line_f.product_qty %>
       	 			
       	 		% endfor
       	 		<% kurang_banget = linc.product_uom_qty - too_dl %>
       	 		<tr>
       	 			<td></td><td>${ linc.mrp_no_kip or '' }</td><td>${ linc.product_id.name or '' }</td><td>${ linc.product_uom_qty or '' }</td>
       	 			<td>${ too_dl or 0 }</td><td>${ kurang_banget or 0 }</td>
       	 		</tr>
       	 		
       	 	% endfor
       	 	
       	 % endfor
       	
       	 </table>
    </body>
</html>
