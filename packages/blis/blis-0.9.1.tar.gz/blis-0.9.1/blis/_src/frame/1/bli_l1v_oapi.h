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


//
// Prototype object-based interfaces.
//

#undef  GENTPROT
#define GENTPROT( opname ) \
\
BLIS_EXPORT_BLIS void PASTEMAC(opname,EX_SUF) \
     ( \
       obj_t*  x, \
       obj_t*  y  \
       BLIS_OAPI_EX_PARAMS  \
     ); 

GENTPROT( addv )
GENTPROT( copyv )
GENTPROT( subv )


#undef  GENTPROT
#define GENTPROT( opname ) \
\
BLIS_EXPORT_BLIS void PASTEMAC(opname,EX_SUF) \
     ( \
       obj_t*  x, \
       obj_t*  index  \
       BLIS_OAPI_EX_PARAMS  \
     );

GENTPROT( amaxv )


#undef  GENTPROT
#define GENTPROT( opname ) \
\
BLIS_EXPORT_BLIS void PASTEMAC(opname,EX_SUF) \
     ( \
       obj_t*  alpha, \
       obj_t*  x, \
       obj_t*  beta, \
       obj_t*  y  \
       BLIS_OAPI_EX_PARAMS  \
     );

GENTPROT( axpbyv )


#undef  GENTPROT
#define GENTPROT( opname ) \
\
BLIS_EXPORT_BLIS void PASTEMAC(opname,EX_SUF) \
     ( \
       obj_t*  alpha, \
       obj_t*  x, \
       obj_t*  y  \
       BLIS_OAPI_EX_PARAMS  \
     ); 

GENTPROT( axpyv )
GENTPROT( scal2v )


#undef  GENTPROT
#define GENTPROT( opname ) \
\
BLIS_EXPORT_BLIS void PASTEMAC(opname,EX_SUF) \
     ( \
       obj_t*  x, \
       obj_t*  y, \
       obj_t*  rho  \
       BLIS_OAPI_EX_PARAMS  \
     ); 

GENTPROT( dotv )


#undef  GENTPROT
#define GENTPROT( opname ) \
\
BLIS_EXPORT_BLIS void PASTEMAC(opname,EX_SUF) \
     ( \
       obj_t*  alpha, \
       obj_t*  x, \
       obj_t*  y, \
       obj_t*  beta, \
       obj_t*  rho  \
       BLIS_OAPI_EX_PARAMS  \
     ); 

GENTPROT( dotxv )


#undef  GENTPROT
#define GENTPROT( opname ) \
\
BLIS_EXPORT_BLIS void PASTEMAC(opname,EX_SUF) \
     ( \
       obj_t*  x  \
       BLIS_OAPI_EX_PARAMS  \
     ); 

GENTPROT( invertv )


#undef  GENTPROT
#define GENTPROT( opname ) \
\
BLIS_EXPORT_BLIS void PASTEMAC(opname,EX_SUF) \
     ( \
       obj_t*  alpha, \
       obj_t*  x  \
       BLIS_OAPI_EX_PARAMS  \
     ); 

GENTPROT( scalv )
GENTPROT( setv )


#undef  GENTPROT
#define GENTPROT( opname ) \
\
BLIS_EXPORT_BLIS void PASTEMAC(opname,EX_SUF) \
     ( \
       obj_t*  x, \
       obj_t*  y  \
       BLIS_OAPI_EX_PARAMS  \
     ); 

GENTPROT( swapv )


#undef  GENTPROT
#define GENTPROT( opname ) \
\
BLIS_EXPORT_BLIS void PASTEMAC(opname,EX_SUF) \
     ( \
       obj_t*  x, \
       obj_t*  beta, \
       obj_t*  y  \
       BLIS_OAPI_EX_PARAMS  \
     );

GENTPROT( xpbyv )

