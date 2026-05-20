package com.google.samples.apps.nowinandroid.core.ui

import android.graphics.RuntimeShader
import android.os.Build
import androidx.compose.animation.core.withInfiniteAnimationFrameMillis
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableFloatStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.ShaderBrush
import androidx.compose.ui.layout.onSizeChanged
import kotlinx.coroutines.isActive

enum class OrbaState(val color: Color) {
    IDLE(Color(0xFFF02DF0)), // Magenta Plasma
    THINKING(Color(0xFFFFFFFF)), // White
    SPEAKING(Color(0xFFFFD700)), // Gold
    LISTENING(Color(0xFFAA00FF)), // Purple Neon
    ANALYZING(Color(0xFF00FFFF)) // Cyan
}

private const val ORBA_SHADER = """
    uniform float2 iResolution;
    uniform float iTime;
    uniform float iVolume;
    uniform half4 iColor;

    // Pseudo-random noise functions for plasma
    float random(vec2 p) {
        return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453123);
    }
    
    float noise(vec2 p) {
        vec2 i = floor(p);
        vec2 f = fract(p);
        f = f * f * (3.0 - 2.0 * f);
        float a = random(i);
        float b = random(i + vec2(1.0, 0.0));
        float c = random(i + vec2(0.0, 1.0));
        float d = random(i + vec2(1.0, 1.0));
        return mix(mix(a, b, f.x), mix(c, d, f.x), f.y);
    }
    
    // Fractal Brownian Motion for swirling clouds
    float fbm(vec2 p) {
        float v = 0.0;
        float a = 0.5;
        vec2 shift = vec2(100.0);
        // Rotation matrix for swirl
        mat2 rot = mat2(cos(0.5), sin(0.5), -sin(0.5), cos(0.5));
        for (int i = 0; i < 5; ++i) {
            v += a * noise(p);
            p = rot * p * 2.0 + shift;
            a *= 0.5;
        }
        return v;
    }

    half4 main(float2 fragCoord) {
        // Normalize coordinates to center
        vec2 uv = (fragCoord.xy - 0.5 * iResolution.xy) / iResolution.y;
        
        float dist = length(uv);
        float radius = 0.35; // Sphere size
        
        vec3 col = vec3(0.0);
        
        // Hardcode base colors to match the image's pink/magenta plasma
        vec3 basePlasma = vec3(0.94, 0.17, 0.94); // Magenta #F02DF0
        vec3 lightPlasma = vec3(1.0, 0.5, 1.0);   // Pink
        vec3 hotSpot = vec3(1.0, 1.0, 1.0);       // White
        
        // 1. Render Sphere Interior
        if (dist < radius) {
            // Map 2D to 3D sphere surface
            vec2 sphereUv = uv / radius;
            float z = sqrt(1.0 - dot(sphereUv, sphereUv));
            vec3 normal = vec3(sphereUv, z);
            
            // Animated texture coordinates
            vec2 p = sphereUv * 2.5;
            p += iTime * 0.15;
            
            // Complex plasma noise
            float n = fbm(p + fbm(p - iTime * 0.1));
            
            // Mix base colors
            vec3 plasmaCol = mix(basePlasma, lightPlasma, n);
            
            // Add glowing hotspots inside the plasma
            float flash = fbm(p * 2.0 + iTime * 0.3);
            flash = smoothstep(0.6, 1.0, flash);
            plasmaCol = mix(plasmaCol, hotSpot, flash * 0.9);
            
            // Add a sharp bright inner rim light
            float rim = 1.0 - max(dot(normal, vec3(0.0, 0.0, 1.0)), 0.0);
            rim = smoothstep(0.5, 1.0, rim);
            plasmaCol += vec3(1.0, 0.7, 1.0) * rim * 1.5;
            
            // Soft outer edge
            float edgeSoftness = smoothstep(radius - 0.02, radius, dist);
            plasmaCol = mix(plasmaCol, basePlasma * 1.5, edgeSoftness);
            
            col = plasmaCol;
        } 
        else {
            // 2. Render Outer Glow
            float glow = radius / dist;
            glow = pow(glow, 2.5) * 0.4;
            col = basePlasma * glow;
        }
        
        // 3. Render Horizontal Lens Flare
        float flareY = abs(uv.y);
        float flareX = abs(uv.x);
        
        // Extremely sharp falloff on Y (thin line), soft on X (wide)
        float flareLine = smoothstep(0.015, 0.0, flareY) * smoothstep(0.9, 0.0, flareX);
        float centralStar = smoothstep(0.1, 0.0, dist) * 1.5;
        
        col += lightPlasma * flareLine;
        col += hotSpot * flareLine * flareLine * 2.0;
        col += hotSpot * centralStar;
        
        // 4. Background Universe
        vec3 bg = vec3(0.12, 0.05, 0.2); // Deep purple space
        if (dist > radius) {
            col = bg + col; // Add glow on top of background
        }
        
        // Audio volume pulse reaction
        col *= 1.0 + (iVolume * 0.15);
        
        return half4(col, 1.0);
    }
"""

@Composable
fun OrbaSphere(
    modifier: Modifier = Modifier,
    state: OrbaState = OrbaState.IDLE,
    volume: Float = 0f // Normalized 0.0 to 1.0
) {
    if (Build.VERSION.SDK_INT < Build.VERSION_CODES.TIRAMISU) {
        // Fallback for API < 33 (could be a simple colored circle or empty)
        Canvas(modifier = modifier.fillMaxSize()) {
            drawCircle(color = state.color)
        }
        return
    }

    val shader = remember { RuntimeShader(ORBA_SHADER) }
    var time by remember { mutableFloatStateOf(0f) }
    var size by remember { mutableStateOf(Size.Zero) }

    LaunchedEffect(Unit) {
        val startTime = System.nanoTime()
        while (isActive) {
            withInfiniteAnimationFrameMillis {
                time = (System.nanoTime() - startTime) / 1_000_000_000f
            }
        }
    }

    Canvas(
        modifier = modifier
            .fillMaxSize()
            .onSizeChanged { size = Size(it.width.toFloat(), it.height.toFloat()) }
    ) {
        if (size == Size.Zero) return@Canvas

        shader.setFloatUniform("iResolution", size.width, size.height)
        shader.setFloatUniform("iTime", time)
        shader.setFloatUniform("iVolume", volume)
        shader.setColorUniform("iColor", state.color.value.toInt())

        drawRect(brush = ShaderBrush(shader))
    }
}
