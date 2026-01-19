// IC Compiler II Version V-2023.12-SP5-1 Verilog Writer
module CHIPTOP_Decoder_inst_design ( SAMPLE , CHIPTOP_instructions_3_ , 
    CHIPTOP_instructions_2_ , CHIPTOP_instructions_1_ , 
    CHIPTOP_instructions_0_ , PRELOAD , EXTEST , CLAMP , BYPASS , 
    place_opt_HFSNET_4 , place_opt_HFSNET_6 ) ;
output SAMPLE ;
input  CHIPTOP_instructions_3_ ;
input  CHIPTOP_instructions_2_ ;
input  CHIPTOP_instructions_1_ ;
input  CHIPTOP_instructions_0_ ;
output PRELOAD ;
output EXTEST ;
output CLAMP ;
output BYPASS ;
input  place_opt_HFSNET_4 ;
input  place_opt_HFSNET_6 ;

INVRTND1BWP7D5T16P96CPD place_opt_HFSINV_160_1933028 ( 
    .I ( place_opt_HFSNET_4 ) , .ZN ( place_opt_HFSNET_3 ) ) ;
ND2SKND1BWP7D5T24P96CPD u_cell_3491 ( .A1 ( place_opt_HFSNET_2 ) , 
    .A2 ( place_opt_HFSNET_1 ) , .ZN ( net1966 ) ) ;
INVRTND1BWP7D5T24P96CPDLVT place_opt_HFSINV_51_1933032 ( 
    .I ( place_opt_HFSNET_6 ) , .ZN ( place_opt_HFSNET_7 ) ) ;
NR3SKPD1BWP7D5T24P96CPD u_cell_3489 ( .A1 ( CHIPTOP_instructions_0_ ) , 
    .A2 ( net1966 ) , .A3 ( CHIPTOP_instructions_1_ ) , .ZN ( BYPASS ) ) ;
NR4SKPRTND1BWP7D5T24P96CPD u_cell_3488 ( .A1 ( place_opt_HFSNET_2 ) , 
    .A2 ( place_opt_HFSNET_1 ) , .A3 ( place_opt_HFSNET_7 ) , 
    .A4 ( CHIPTOP_instructions_0_ ) , .ZN ( CLAMP ) ) ;
NR3SKPD1BWP7D5T24P96CPD u_cell_3487 ( .A1 ( net1966 ) , 
    .A2 ( place_opt_HFSNET_7 ) , .A3 ( place_opt_HFSNET_3 ) , .ZN ( EXTEST ) ) ;
NR3SKPD1BWP7D5T24P96CPD u_cell_3486 ( .A1 ( net1966 ) , 
    .A2 ( place_opt_HFSNET_5 ) , .A3 ( CHIPTOP_instructions_1_ ) , 
    .ZN ( SAMPLE ) ) ;
BUFFSKPD1BWP7D5T24P96CPD u_cell_3496 ( .I ( SAMPLE ) , .Z ( PRELOAD ) ) ;
INVRTND1BWP7D5T24P96CPDLVT place_opt_HFSINV_243_1701376 ( 
    .I ( CHIPTOP_instructions_2_ ) , .ZN ( place_opt_HFSNET_1 ) ) ;
INVRTND1BWP7D5T24P96CPDLVT place_opt_HFSINV_281_1701377 ( 
    .I ( CHIPTOP_instructions_3_ ) , .ZN ( place_opt_HFSNET_2 ) ) ;
INVRTND1BWP7D5T16P96CPD place_opt_HFSINV_267_1933030 ( 
    .I ( place_opt_HFSNET_4 ) , .ZN ( place_opt_HFSNET_5 ) ) ;
endmodule