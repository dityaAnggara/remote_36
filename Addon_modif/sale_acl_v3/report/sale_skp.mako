<html>
    <head>
        <title>Surat Kontrak Penjualan</title>
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
        <div id="idiv1">
            <div id="idiv6">
                <ol>
                    % for order in objects:
	                    % if order.po_sl == True:
		                    % for line in order.order_line:
		                    <table>
		                        <tr>
		                            <td rowspan="7"><li>&nbsp;</li></td>
		                        <td>Nama Barang</td>
		                        <td>:</td>
		                        <td colspan="7" class="boldest mono">${ line.name or '' }(KIP:${ line.mrp_no_kip or '' })</td>
		                        </tr>
		                        <tr>
		                            <td>Model</td>
		                            <td>:</td>
		                            <td class="boldest mono">${ line.product_id.model or ''}</td>
		                            <td>No.PO</td>
		                            <td>:</td>
		                            <td class="boldest mono">${ line.purchase_customer_no or ''}</td>
		                            <td>&nbsp;</td>
		                            <td>&nbsp;</td>
		                            <td class="boldest mono">&nbsp;</td>
		                        </tr>
		                        <tr>
		                            <td>Ukuran</td>
		                            <td>:</td>
		                            <td class="boldest mono">${ line.product_id.dimension or ''}</td>
		                            <td>Subs</td>
		                            <td>:</td>
		                            <td class="boldest mono">${ line.product_id.subtance or ''}</td>
		                            <td>Flute</td>
		                            <td>:</td>
		                            <td class="boldest mono">${ line.product_id.flute or ''}</td>
		                        </tr>
		                        <tr>
		                            <td>Jml.Order</td>
		                            <td>:</td>
		                            <td class="boldest mono">${ line.product_uom_qty or ''} Pcs</td>
		                            <td>Franco</td>
		                            <td>:</td>
		                            <td class="boldest mono">${ order.partner_id.franco_true or ''}</td>
		                            <td>Disc%</td>
		                            <td>:</td>
		                            <td class="boldest mono">${ line.discount or ''}</td>
		                        </tr>
		                        <tr>
		                            <td>Harga/set</td>
		                            <td>:</td>
		                            <td class="boldest mono">Rp. ${ line.price_unit or '0' }</td>
		                            <td>Warna</td>
		                            <td>:</td>
		                            <td class="boldest mono">${ line.product_id.color or ''}</td>
		                            <td>K.Trm</td>
		                            <td>:</td>
		                            <td class="boldest mono">${ order.payment_term or ''} Hr</td>
		                        </tr>
		                        <tr>
		                            <td>Tgl kirim</td>
		                            <td>:</td>
		                            <td class="boldest mono"></td>
		                            <td>Jml Kirim</td>
		                            <td>:</td>
		                            <td class="boldest mono">${ line.product_uom_qty or ''} Pcs</td>
		                            <td>&nbsp;</td>
		                            <td>&nbsp;</td>
		                            <td class="boldest mono">&nbsp;</td>
		                        </tr>
		                        <tr>
		                            <td colspan="9">Catatan : <span class="mono boldest"><br /><br /></span></td>
		                        </tr>
		                    </table>
		                    % endfor
		                % endif    
                    % endfor
                </ol>
            </div>
        </div>
    </body>
</html>
