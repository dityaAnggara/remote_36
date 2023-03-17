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
	  <center><U><h4><font size="5">Surat Jalan</font></h4></U></center>
	  
	  % for picking in objects:
	   			
	   			<p>${ picking.partner_id.name or '' }</br>${ picking.partner_id.address or '' }</p>
	   			
	   			
	  % endfor
	  <table width=1000 border="1">
	  <tr>
	   			<th>JENIS BARANG</th><th>Jumlah Satuan</th><th>Keterangan</th>
	   		</tr>
	  % for picking in objects:
	  	% for movee in picking.move_lines:
	   		
	   		<tr>
	   			<td>${ movee.name or '' }</td>
	   			<td>${ movee.product_qty or '' } pcs</td>
	   			<td>${ picking.jumlah_ikat or '' }
	   			</br>${ picking.b_kend or '' }</br>
	   			${ picking.b_bruto or '' }</br>
	   			${ picking.b_netto or '' }</td>
	   		</tr>	
	  	% endfor
	  % endfor
	  </table>
	  
	  </table>	
	</body>
</html>