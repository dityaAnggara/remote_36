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
      % for invc in account_inv():
      <p>Kode dan Nomer Seri Faktur Pajak : ${ invc.no_faktur or '' }</p>
      <p>Pengusaha Kena Pajak</p>
      <p>nama : ${ invc.company_id.partner_id.name or '' }</p>
      <p>Alamat : ${ invc.company_id.partner_id.street or '' } ${ invc.company_id.partner_id.street2 or '' } ${ invc.company_id.partner_id.city or '' } ${ invc.company_id.partner_id.state_id.name or '' }
      ${ invc.company_id.partner_id.zip or '' } ${ invc.company_id.partner_id.country_id.name or '' } ${ invc.company_id.partner_id.franco_true or '' }  
      </p>
      <p>NPWP : ${ invc.company_id.partner_id.npwp_acl or '' }</p>
      <p>Pembeli Barang Kena Pajak/Penerima Jasa Kena Pajak</p>
      <p>nama : ${ invc.partner_id.name or '' }</p>
      <p>Alamat : ${ invc.partner_id.street or '' } ${ invc.partner_id.street2 or '' } ${ invc.partner_id.city or '' } ${ invc.partner_id.state_id.name or '' }
      ${ invc.partner_id.zip or '' } ${ invc.partner_id.country_id.name or '' } ${ invc.partner_id.franco_true or '' }  
      </p>
      <p>NPWP : ${ invc.partner_id.npwp_acl or '' }</p>
      % endfor
      <table>
      <tr><th>No Urut</th><th>Nama Barang Kena Pajak/Jasa Kena Pajak</th><th>Harga Jual/Penggantian/Uang Muka/Termin(Rp)</th></tr>
      <% no=1 %>
      <% xali_tot = 0 %>
      
      % for innv in account_inv():
      	% for lininv in innv.invoice_line:
			<% xali = lininv.quantity * lininv.price_unit %>      	
      		<tr><td>${no}</td>
      		<td>${ lininv.product_id.name or '' } ${ lininv.product_id.model or '' } ${ lininv.product_id.dimension or '' } ${ lininv.product_id.subtance or '' }
      		${ lininv.product_id.flute or '' } ${ lininv.product_id.color or '' } ${ lininv.quantity or '' } pcs ${ lininv.price_unit or '' }   
      		</td> 
      		<td>${ xali or '' }</td>
      		</tr>
      		<% no += no %>	
      	% endfor
      % endfor
      </table>
      % for iv in account_inv():
      	 <% dicount = 0 %>
        % for linvo in acn_line_one(iv.id):
        	<% dfoo = acn_ln_bw(linvo) %>
        	<% dicount += dfoo.discount %>	
        % endfor
         
      	<p>Harga Jual/Penggantian/Uang Muka/Termin(Rp) ${ iv.amount_total or '' }</p>
       	<p>Dikurangi Potongan Harga ${ dicount or '' }</p>
      % endfor
      <% amnt_dp = 0 %>
      % for purp in satu():
      	<% bpkl = dua(purp) %>
      	<% amnt_dp += bpkl.amount_total %>
      % endfor
      <p>Dikurangi Uang Muka yang telah diterima ${ amnt_dp or '' }</p>
      % for ivone in account_inv():
      	<p>Dasar Pengenaan Pajak ${ ivone.amount_total or '' }</p>
       
      % endfor
    </body>
</html>
