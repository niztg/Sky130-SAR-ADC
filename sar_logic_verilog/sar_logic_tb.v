`timescale 1ns/1ps

module sar_logic_tb;

    real V_sample = 1.5;
    real V_ref    = 1.8;
    integer N     = 10;

    reg        clk;
    reg        rst;
    reg        start;
    reg        comp_in;
    wire [9:0] cdac_sw;
    wire [9:0] result;
    wire       done;

    sar_logic dut (
        .clk(clk), .rst(rst), .start(start),
        .comp_in(comp_in), .cdac_sw(cdac_sw),
        .result(result), .done(done)
    );

    initial clk = 0;
    always #5 clk = ~clk;

    real V_dac, V_dac_next;
    integer i, expected;

    initial begin
        rst = 1; start = 0; comp_in = 0;
        @(posedge clk); #1;
        rst = 0;

        @(posedge clk); #1;
        start = 1;
        @(posedge clk); #1;
        start = 0;

        V_dac = 0.0;
        for (i = N-1; i >= 0; i = i - 1) begin
            V_dac_next = V_dac + V_ref / (2.0 ** (N - i));
            if (V_sample >= V_dac_next) begin
                comp_in = 1;
                V_dac   = V_dac_next;
            end else begin
                comp_in = 0;
            end
            @(posedge clk); #1;
        end

        expected = $rtoi(V_sample / V_ref * 1024);
        $display("Expected: %0d | Got: %0d | %s",
            expected, result,
            (result == expected) ? "PASS" : "FAIL");
        $finish;
    end

endmodule