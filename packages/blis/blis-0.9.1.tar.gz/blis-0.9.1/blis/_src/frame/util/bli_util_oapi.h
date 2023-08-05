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

#undef  GENPROT
#define GENPROT( opname ) \
\
BLIS_EXPORT_BLIS void PASTEMAC(opname,EX_SUF) \
     ( \
       obj_t*  x, \
       obj_t*  asum  \
       BLIS_OAPI_EX_PARAMS  \
     );

GENPROT( asumv )


#undef  GENPROT
#define GENPROT( opname ) \
\
BLIS_EXPORT_BLIS void PASTEMAC(opname,EX_SUF) \
     ( \
       obj_t*  a  \
       BLIS_OAPI_EX_PARAMS  \
     );

GENPROT( mkherm )
GENPROT( mksymm )
GENPROT( mktrim )


#undef  GENPROT
#define GENPROT( opname ) \
\
BLIS_EXPORT_BLIS void PASTEMAC(opname,EX_SUF) \
     ( \
       obj_t*  x, \
       obj_t*  norm  \
       BLIS_OAPI_EX_PARAMS  \
     );

GENPROT( norm1v )
GENPROT( normfv )
GENPROT( normiv )


#undef  GENPROT
#define GENPROT( opname ) \
\
BLIS_EXPORT_BLIS void PASTEMAC(opname,EX_SUF) \
     ( \
       obj_t*  x, \
       obj_t*  norm  \
       BLIS_OAPI_EX_PARAMS  \
     );

GENPROT( norm1m )
GENPROT( normfm )
GENPROT( normim )


#undef  GENPROT
#define GENPROT( opname ) \
\
BLIS_EXPORT_BLIS void PASTEMAC(opname,EX_SUF) \
     ( \
       obj_t*  x  \
       BLIS_OAPI_EX_PARAMS  \
     );

GENPROT( randv )
GENPROT( randnv )


#undef  GENPROT
#define GENPROT( opname ) \
\
BLIS_EXPORT_BLIS void PASTEMAC(opname,EX_SUF) \
     ( \
       obj_t*  x  \
       BLIS_OAPI_EX_PARAMS  \
     );

GENPROT( randm )
GENPROT( randnm )


#undef  GENPROT
#define GENPROT( opname ) \
\
BLIS_EXPORT_BLIS void PASTEMAC(opname,EX_SUF) \
     ( \
       obj_t*  x, \
       obj_t*  scale, \
       obj_t*  sumsq  \
       BLIS_OAPI_EX_PARAMS  \
     );

GENPROT( sumsqv )

// -----------------------------------------------------------------------------

// Operations with basic interfaces only.

#ifdef BLIS_OAPI_BASIC

/*
#undef  GENPROT
#define GENPROT( opname ) \
\
BLIS_EXPORT_BLIS void PASTEMAC0(opname) \
     ( \
       obj_t*  chi, \
       obj_t*  psi, \
       bool*   is_eq  \
     );

GENPROT( eqsc )


#undef  GENPROT
#define GENPROT( opname ) \
\
BLIS_EXPORT_BLIS void PASTEMAC0(opname) \
     ( \
       obj_t*  x, \
       obj_t*  y, \
       bool*   is_eq  \
     );

GENPROT( eqv )
*/


#undef  GENPROT
#define GENPROT( opname ) \
\
BLIS_EXPORT_BLIS void PASTEMAC0(opname) \
     ( \
       obj_t*  x, \
       obj_t*  y, \
       bool*   is_eq  \
     );

GENPROT( eqsc )
GENPROT( eqv )
GENPROT( eqm )


#undef  GENPROT
#define GENPROT( opname ) \
\
BLIS_EXPORT_BLIS void PASTEMAC0(opname) \
     ( \
       FILE*   file, \
       char*   s1, \
       obj_t*  x, \
       char*   format, \
       char*   s2  \
     );

GENPROT( fprintv )
GENPROT( fprintm )


#undef  GENPROT
#define GENPROT( opname ) \
\
BLIS_EXPORT_BLIS void PASTEMAC0(opname) \
     ( \
       char*   s1, \
       obj_t*  x, \
       char*   format, \
       char*   s2  \
     );

GENPROT( printv )
GENPROT( printm )

#endif // #ifdef BLIS_OAPI_BASIC

