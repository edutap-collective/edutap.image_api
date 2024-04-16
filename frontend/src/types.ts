export enum MaskEnum {
    BOX = "box",
    CIRCLE = "circle",
    NONE = "none"
}

export enum AspectRatioEnum {
    SQUARE = "square",
    PORTRAIT = "portrait",
    FREE = "free"
}

export type CropData = {
    mask: MaskEnum
    aspectRatio: AspectRatioEnum
    height: number
    width: number | "auto"
    radius: number
}