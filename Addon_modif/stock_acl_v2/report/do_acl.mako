<html>
	<head>
	
	 <style>
	 	body{
	 		font-family:helvetica; 
	 		font-size:8;
	 	}
	 </style>
	</head>
	<body style="font-family:helvetica; font-size:8;">
		<div style="margin-top:200px;margin-left:20px;">
			% for picking in objects:
	   			No DO:
	   			${ picking.gen_do or '' } </br>
	   			Bagian Gudang </br>
	   			Tanggal : ${ picking.delivery_date or '' }</br>
	   			No SKP: ${ picking.sale_id.po_sl or '' }</br>
	   			<p>Customer data:
	   			${ picking.partner_id.name or '' }
	   			${ picking.partner_id.street or '' }
	   			${ picking.partner_id.street2 or '' }
	   			${ picking.partner_id.city or '' }
	   			${ picking.partner_id.state_id.name or '' }
	   			${ picking.partner_id.zip or '' }
	   			${ picking.partner_id.franco or '' }
	   			</p>
	  % endfor
		</div>
		<table border="2">
 		<th rowspan="3">No</th><th rowspan="3">Jenis Barang</th>
		<th rowspan="3">Satuan</th><th colspan="4">Kwantitas</th><th rowspan="3">Keterangan</th><tr><th rowspan="2">Pesanan</th>
	<th colspan="2" >Realisasi</th><th rowspan="2">Sisa</th></tr>
	<tr><th>Saat Ini</th><th>Kumulatif s/d saat ini</th></tr>
		 <% no=1 %> 		
	  % for picking in objects:
	  	% for movee in picking.move_lines:
	   		<% trr = (movee.total_permintaan) - (movee.marketing_request_quantity) %>
	   		<% trs = (movee.total_permintaan) - (movee.warehouse_realise) %>
	   		<tr>
	   		    <td>${no}</td>
	   			<td>${ movee.name or '' }</br>
	   			</td>
	   			<td>pcs</td>
	   			<td>${ movee.total_permintaan or '' }</td>
	   			<td>${ movee.marketing_request_quantity or '' }</td>
	   			<td>${ trr or '' }</td>
	   			<td>${ trs or '' }</td>
	   			<td></td>
	   		</tr>
	   		<% no += no %>	
	  	% endfor
	  % endfor
	</table>
	</body>
</html>