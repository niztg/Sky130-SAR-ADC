module sar_logic (
    input  wire        clk,
    input  wire        rst,
    input  wire        start,
    input  wire        comp_in,
    output reg  [9:0]  cdac_sw,
    output reg  [9:0]  result,
    output reg         done
);

    reg [3:0] bit_idx;  // counts from 9 down to 0
    reg       active;   // conversion in progress

    always @(posedge clk or posedge rst) begin
        if (rst) begin
            cdac_sw <= 10'b0;
            result  <= 10'b0;
            done    <= 1'b0;
            active  <= 1'b0;
            bit_idx <= 4'd9;
        end
        else if (start && !active) begin
            cdac_sw <= 10'b0;
            result  <= 10'b0;
            done    <= 1'b0;
            active  <= 1'b1;
            bit_idx <= 4'd9;
            cdac_sw[9] <= 1'b1;  // assert MSB trial
        end
        else if (active) begin
            // record comparator decision for current bit
            if (comp_in)
                result[bit_idx] <= 1'b1;
            else
                result[bit_idx] <= 1'b0;

            // clear trial bit if comparator said no
            cdac_sw[bit_idx] <= comp_in;

            if (bit_idx == 4'd0) begin
                // last bit done
                active  <= 1'b0;
                done    <= 1'b1;
                cdac_sw <= 10'b0;
            end
            else begin
                bit_idx <= bit_idx - 1;
                cdac_sw[bit_idx - 1] <= 1'b1;  // assert next trial bit
            end
        end
    end

endmodule