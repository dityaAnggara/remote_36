<html>
	<head>
	<script> function subst() { var vars={}; var x=document.location.search.substring(1).split('&'); for(var i in x) {var z=x[i].split('=',2);vars[z[0]] = unescape(z[1]);} var x=['frompage','topage','page','webpage','section','subsection','subsubsection']; for(var i in x) { var y = document.getElementsByClassName(x[i]); for(var j=0; j<y.length; ++j) y[j].textContent = vars[x[i]]; } } </script>
	 <style type="text/css"> 
	 body {
font-family:helvetica;
font-size:12;
}


.dest_address {
margin-left:60%;
font-size:12;
}
.header {
margin-left:0;
text-align:left;
width:300px;
font-size:12;
}

.title {
font-size:16;
font-weight: bold;

}


.basic_table{
text-align:center;
border:1px solid lightGrey;
border-collapse: collapse;
}
.basic_table td {
border:1px solid lightGrey;
font-size:12;


}

.list_table {
border-color:black;
text-align:center;
border-collapse: collapse;

}
.list_table td {
border-color:gray;
border-top:1px solid gray;
text-align:left;
font-size:12;
padding-right:3px
padding-left:3px
padding-top:3px
padding-bottom:3px
}

.list_table th {
border-bottom:2px solid black;
text-align:left;
font-size:12;
font-weight:bold;
padding-right:3px
padding-left:3px
}

.list_tabe thead {
    display:table-header-group;
}


.total {
width:100%;
}
.lib {
width:10.3%;
}
.tot {
text-align:right;
width:15%;
}
.lefttot {
width:74%;
}
.tax {
width:50%;
} 
	 </style>
	</head>
	<body>
		<table class="header" style="border-bottom: 0px solid black; width: 100%"> 
		<tr> <td>${helper.embed_logo_by_name('camptocamp_logo')|n}</td> <td style="text-align:right"> </td> </tr> 
		<tr> <td><br/></td> <td style="text-align:right"> </td> </tr> <tr> <td>${company.partner_id.name |entity}</td> <td/> </tr> 
		<tr> <td >${company.partner_id.street or ''|entity}</td> <td/> </tr> 
		<tr> <td>Phone: ${company.partner_id.phone or ''|entity} </td> <td/> </tr> 
		<tr> <td>Mail: ${company.partner_id.email or ''|entity}<br/></td> </tr> 
		<table>
		% for order in objects:
		<tr>
		<td>${order.po_sl}</td>
		<td>${order.partner_id.name}</td>
		<td>${order.partner_id.street or ''}</td>
		<td>${order.partner_id.street2 or ''}</td>
		<td>${order.partner_id.zip or ''} </td>
		<td>${order.partner_id.x_npwp or ''}</td>
		</tr>
	% endfor	
		</table>
		</table>
		
	</body>
</html>