"""
Constants and configuration for Viewport Playblast.
"""

# Linux default ffmpeg path
DEFAULT_FFMPEG_PATH = "/usr/bin/ffmpeg"

RESOLUTION_LOOKUP = {
    "Render": (),
    "HD 1080": (1920, 1080),
    "HD 720": (1280, 720),
    "HD 540": (960, 540),
}

FRAME_RANGE_PRESETS = [
    "Render",
    "Playback",
    "Animation",
]

VIDEO_ENCODER_LOOKUP = {
    "mov": ["h264"],
    "mp4": ["h264"],
    "Image": ["jpg", "png", "tif"],
}

H264_QUALITIES = {
    "Very High": 18,
    "High": 20,
    "Medium": 23,
    "Low": 26,
}

H264_PRESETS = [
    "veryslow",
    "slow",
    "medium",
    "fast",
    "faster",
    "ultrafast",
]

VIEWPORT_VISIBILITY_LOOKUP = [
    ["Controllers", "controllers"],
    ["NURBS Curves", "nurbsCurves"],
    ["NURBS Surfaces", "nurbsSurfaces"],
    ["NURBS CVs", "cv"],
    ["NURBS Hulls", "hulls"],
    ["Polygons", "polymeshes"],
    ["Subdiv Surfaces", "subdivSurfaces"],
    ["Planes", "planes"],
    ["Lights", "lights"],
    ["Cameras", "cameras"],
    ["Image Planes", "imagePlane"],
    ["Joints", "joints"],
    ["IK Handles", "ikHandles"],
    ["Deformers", "deformers"],
    ["Dynamics", "dynamics"],
    ["Particle Instancers", "particleInstancers"],
    ["Fluids", "fluids"],
    ["Hair Systems", "hairSystems"],
    ["Follicles", "follicles"],
    ["nCloths", "nCloths"],
    ["nParticles", "nParticles"],
    ["nRigids", "nRigids"],
    ["Dynamic Constraints", "dynamicConstraints"],
    ["Locators", "locators"],
    ["Dimensions", "dimensions"],
    ["Pivots", "pivots"],
    ["Handles", "handles"],
    ["Texture Placements", "textures"],
    ["Strokes", "strokes"],
    ["Motion Trails", "motionTrails"],
    ["Plugin Shapes", "pluginShapes"],
    ["Clip Ghosts", "clipGhosts"],
    ["Grease Pencil", "greasePencils"],
    ["Grid", "grid"],
    ["HUD", "hud"],
    ["Hold-Outs", "hos"],
    ["Selection Highlighting", "sel"],
]

VIEWPORT_VISIBILITY_PRESETS = {
    "Viewport": [],
    "Geo": ["NURBS Surfaces", "Polygons"],
    "Dynamics": ["NURBS Surfaces", "Polygons", "Dynamics", "Fluids", "nParticles"],
}

DEFAULT_CAMERA = None
DEFAULT_RESOLUTION = "Render"
DEFAULT_FRAME_RANGE = "Render"

DEFAULT_CONTAINER = "mp4"
DEFAULT_ENCODER = "h264"
DEFAULT_H264_QUALITY = "High"
DEFAULT_H264_PRESET = "fast"
DEFAULT_IMAGE_QUALITY = 100

DEFAULT_VISIBILITY = "Viewport"

DEFAULT_PADDING = 4

VERSION = "1.0.0"
