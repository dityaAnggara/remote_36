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
	  <center><U><h4><font size="5">Keterangan Muat Barang</font></h4></U></center>
	  <table  width="1000">
	  % for picking in objects:
	   			<tr>
	   			<td>Customer :</td><td>${ picking.partner_id.name or '' }</td><td></td><td></td>
	   			</tr>
	   			<tr>
	   			<td>No :</td><td></td><td>No Kendaraan :</td><td>${ picking.no_kendaraan or '' }</td>
	   			</tr>
	   			<tr>
	   			<td>Tgl :</td><td>${ picking.delivery_date or ''}</td>
	   			<td>Pengangkutan:</td><td>${ picking.jasa_angkut.name or '' }</td>
	   			</tr>
	   			<tr>
	   			<td>Nama Sopir :</td><td>${ picking.sopir or ''}</td>
	   			<td>No DO :</td><td>${ picking.gen_do or '' }</td>
	   			</tr>
	   			<tr>
	   			<td>Tgl Muat :</td><td>${ picking.delivery_date or ''}</td>
	   			<td>No SO :</td><td>${ picking.sale_id.po_sl or '' }</td>
	   			</tr>
	   			
	  % endfor
	  <table width=1000 border="1">
	  <tr>
	   			<th>JENIS BARANG</th><th>Satuan</th><th>Jumlah</th><th>Keterangan</th>
	   		</tr>
	  % for picking in objects:
	  	% for movee in picking.move_lines:
	   		
	   		<tr>
	   			<td>${ movee.name or '' }</td>
	   			<td>pcs</td>
	   			<td>${ movee.product_qty or '' }</td>
	   			<td>${ picking.jumlah_ikat or '' }</td>
	   		</tr>	
	  	% endfor
	  % endfor
	  </table>
	  
	  </table>	
	</body>
</html>