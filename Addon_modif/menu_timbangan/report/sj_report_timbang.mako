<!DOCTYPE html>
<!--
<%
import base64
import mx.DateTime

def oe_datetime_format(obj,format='%Y-%m-%d %H:%M:%S'):
    if obj.val:
        if hasattr(obj,'name') and (obj.name):
            return mx.DateTime.strptime(obj.name,format)
        else:
            return false
    else:
        return false
%>
-->
<html>
    <head>
        <title>Surat Jalan</title>
        <style type="text/css">
            body {
                margin: 0px;
                padding: 0px;
                font-size: 10px;
                font-family: arial, sans-serif, helvetica;
                /* line-height: 17px; */
            }
            table {
                border-collapse: collapse;
                border: none;
                margin: 0px;
                padding: 0px;
            }
            tr, td, th {
                margin: 0px;
                padding: 0px;
            }
            .main-tab {
                width: 100%;
            }
            .main-tab th, .main-tab td {
                border: 1px solid;
                padding: 5px;
            }
            .main-tab td {
                vertical-align: top;
            }
            .main-tab tr:first-child th {
                border-top: 3px double;
            }
            .main-tab th:first-child, .main-tab td:first-child {
                border-left: none;
            }
            .main-tab th:last-child, .main-tab td:last-child {
                border-right: none;
            }
            .main {
                display: block;
                border: 1px solid;
            }
            .fix-tab {
                table-layout: fixed;
            }
            .head-tab {
                width: 100%;
            }
            .head-tab td {
                padding: 5px;
                vertical-align: top;
            }
            .head-tab td table {
                width: 100%;
            }
            .head-tab td table td {
                padding: 0px;
            }
            .foot-tab {
                width: 100%;
            }
            .foot-tab td {
                padding: 5px;
                vertical-align: top;
            }
            .full-block {
                display: block;
                width: 100%;
                clear: both;
            }
            .ins-tab {
                width: 100%;
                padding: 0px;
            }
            .ins-tab td {
                border: none;
                padding: 0px;
            }
            .ins-tab td:last-of-type {
                text-align: right;
            }
            .mtd {
                width: 10px;
            }
            .mtd2 {
                width: 80px;
            }
            .dtuju {
                padding: 5px;
                border: 1px solid;
                border-radius: 5px;
                height: 90px;
                text-align: justify;
                word-break: break-all;
                text-transform: capitalize;
                overflow: hidden;
            }
        </style>
    </head>
    <body>
        <br />&nbsp;<br />
        % for picking in objects:
	        % if picking.surat_jalan != False:
	        <div class="main">
	            <table class="head-tab fix-tab">
	                <tr>
	                    <td>
	                        <div class="full-block">
	                            <div style="display: inline-block; float: left;">${ helper.embed_image('png',picking.company_id.logo,width=40) or '' }</div>
	                            <span style="font-size: 14px; font-weight: 900;">${ picking.company_id and picking.company_id.name or '' }</span><br />
	                            <span style="font-weight: 900;">${ picking.company_id and picking.company_id.rml_header1 or '' }</span>
	                        </div>
	                    </td>
	                    <td style="text-align: center;">
	                        <div style="font-weight: 900;">Asli Harap Dikembalikan</div>
	                        <div style="font-weight: 900; font-size: 16px">SURAT JALAN</div>
	                    </td>
	                    <td rowspan="4">
	                        <div style="text-align: right; font-size: 12px; font-weight: 900;">No.${ picking.surat_jalan or ' - ' }</div>
	                        <div class="dtuju">
	                            Kepada yang terhormat,<br />
	                            ${ picking.partner_id and picking.partner_id.name or '' }<br />
	                            ${ picking.partner_id and picking.partner_id.street or '' }
	                            ${ picking.partner_id and picking.partner_id.street2 or '' }
	                            ${ picking.partner_id and picking.partner_id.city or '' }
	                            ${ picking.partner_id and picking.partner_id.state_id and picking.partner_id.state_id.name or '' }
	                            ${ picking.partner_id and picking.partner_id.country_id and picking.partner_id.country_id.name or '' }
	                        </div>
	                    </td>
	                </tr>
	                <tr>
	                    <td>Bersama ini kami kirimkan barang-barang seperti tercantum di bawah ini dengan</td>
	                    <td>&nbsp;</td>
	                </tr>
	                <tr>
	                    <td>
	                        <table class="ins-tab fix-tab">
	                            <tr>
	                                <td class="mtd2">Pengangkutan</td>
	                                <td class="mtd">:</td>
	                                <td>${ picking.jasa_angkut or '' }</td>
	                            </tr>
	                        </table>
	                    </td>
	                    <td>
	                        <table class="ins-tab fix-tab">
	                            <tr>
	                                <td class="mtd2">Ref. No. &amp; Tgl.</td>
	                                <td class="mtd">:</td>
	                                <td>${ picking.name or '' }</td>
	                            </tr>
	                        </table>
	                    </td>
	                </tr>
	                <tr>
	                    <td>
	                        <table class="ins-tab fix-tab">
	                            <tr>
	                                <td class="mtd2">Kendaraan No.</td>
	                                <td class="mtd">:</td>
	                                <td>${ picking.no_kendaraan or '' }</td>
	                            </tr>
	                        </table>
	                    </td>
	                    <td>
	                        <table class="ins-tab fix-tab">
	                            <tr>
	                                <td class="mtd2">Ref. No. &amp; Tgl.</td>
	                                <td class="mtd">:</td>
	                                <td>${ picking.name or '' }</td>
	                            </tr>
	                        </table>
	                    </td>
	                </tr>
	            </table>
	            <table class="main-tab fix-tab">
	                <thead>
	                    <tr>
	                        <th style="width: 30px;">No.</th>
	                        <th>Jenis Barang</th>
	                        <th style="width: 120px;">Jumlah<br />Satuan</th>
	                        <th>Keterangan</th>
	                    </tr>
	                </thead>
	                <tbody>
	                    <% i = 1 %>
	                    % for line in picking.move_line_new:
	                    <tr>
	                        <td style="text-align: center;">${ i or '' }</td>
	                        <td>${ line.name or '' }</td>
	                        <td style="text-align: center;">${ line.warehouse_realise or '0' } ${ line.product_uom and line.product_uom.name or '' }</td>
	                        <td>${ line.prepare_delivery or '' }<br />${ line.take_over or '' }</td>
	                    </tr>
	                    <% i = i + 1 %>
	                    % endfor
	                    <tr>
	                        <td>&nbsp;</td>
	                        <td>&nbsp;</td>
	                        <td>&nbsp;</td>
	                        <td>
	                            <table class="ins-tab fix-tab">
	                                <tr>
	                                    <td>B.KEND</td>
	                                    <td>:</td>
	                                    <td style="text-align: right;">
	                                    	${ picking.b_kend or 0 }
	                                    	Kg
	                                    </td>
	                                </tr>
	                                <tr>
	                                    <td>B.BRUTO</td>
	                                    <td>:</td>
	                                    <td style="text-align: right;">
	                                    	${ picking.b_bruto or 0 }
	                                    	Kg
	                                    </td>
	                                </tr>
	                                <tr>
	                                    <td>B.NETTO</td>
	                                    <td>:</td>
	                                    <td style="text-align: right;">
	                                    	${ picking.b_netto or 0 }
	                                    	Kg
	                                    </td>
	                                </tr>
	                            </table>
	                        </td>
	                    </tr>
	                </tbody>
	            </table>
	            <table class="head-tab fix-tab">
	            	<tr>
	            		<td style="text-align: center;">
	            			Telah diterima dalam keadaan baik<br />
							dengan jumlah yang betul oleh,<br />
	            			Tgl, ${ oe_datetime_format(picking.date).strftime('%d %B %Y') or '' }
	            			<br /><br /><br /><br /><br />
	            			(............................................................)<br />
	            			Nama terang &amp; stempel perusahaan
	            		</td>
	            		<td style="text-align: center;">
	            			Pengemudi,<br /><br /><br /><br /><br /><br /><br />
	            			(............................................................)<br />
	            			Nama terang
						</td>
	            		<td style="text-align: center;">
	            			Tangerang, ${ oe_datetime_format(picking.date).strftime('%d %B %Y') or '' }<br />
	            			Dibuat oleh,<br /><br /><br /><br /><br /><br />
	            			(............................................................)
	            		</td>
	            	</tr>
	            </table>
	            <hr />
	            <table class="foot-tab">
	            	<tr>
	            		<td>Catatan</td>
	            		<td>:</td>
	            		<td>
	            			Barang-barang yang telah keluar dari gudang diluar tanggung jawab pengirim.<br />
	            			Lembar ASLI Surat Jalan ini harap dikirimkan kembali ke Pengirim dalam waktu 3 (tiga) hari sejak tanggal penerimaan barang.<br />
	            			Hak kepemilikan atas barang-barang tersebut tetap berada pada kami.
	            		</td>
	            	</tr>
	            <table>
	        </div>
	        % endif
        % endfor
    </body>
</html>
