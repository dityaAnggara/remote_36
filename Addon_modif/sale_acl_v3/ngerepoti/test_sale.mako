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
      % for apd in apen_test(ctx):
      	<% df = bws(apd) %>
      	% for pick_i in pick(df.id):
      		<% fg = pick_line(pick_i) %>
      		No SO: ${ fg.origin or none }, NO SJ: ${ fg.surat_jalan or none }<br /> 
      	% endfor	
      % endfor
    	
    </body>
</html>
