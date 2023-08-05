/*

   BLIS
   An object-based framework for developing high-performance BLAS-like
   libraries.

   Copyright (C) 2014, The University of Texas at Austin

   Redistribution and use in source and binary forms, with or without
   modification, are permitted provided that the following conditions are
   met:
    - Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    - Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
    - Neither the name(s) of the copyright holder(s) nor the names of its
      contributors may be used to endorse or promote products derived
      from this software without specific prior written permission.

   THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
   "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
   LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
   A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
   HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
   SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
   LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
   DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
   THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
   (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
   OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

*/

#undef  GENTPROT
#define GENTPROT( ctype, ch, varname ) \
\
void PASTEMAC(ch,varname) \
     ( \
       struc_t         strucc, \
       diag_t          diagc, \
       uplo_t          uploc, \
       conj_t          conjc, \
       pack_t          schema, \
       bool            invdiag, \
       dim_t           panel_dim, \
       dim_t           panel_len, \
       dim_t           panel_dim_max, \
       dim_t           panel_len_max, \
       dim_t           panel_dim_off, \
       dim_t           panel_len_off, \
       ctype* restrict kappa, \
       ctype* restrict c, inc_t incc, inc_t ldc, \
       ctype* restrict p,             inc_t ldp, \
                          inc_t is_p, \
       cntx_t*         cntx  \
     );

INSERT_GENTPROT_BASIC0( packm_struc_cxk )
INSERT_GENTPROT_BASIC0( packm_herm_cxk )
INSERT_GENTPROT_BASIC0( packm_tri_cxk )

