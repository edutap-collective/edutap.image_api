import {SubmitHandler, useForm} from "react-hook-form";
import clsx from "clsx";
import {AspectRatioEnum, CropData, MaskEnum} from "../types.ts";

interface ConfigFormProps {
    onSubmit: SubmitHandler<CropData>
    onReset: () => void
}

const ConfigForm = ({onSubmit, onReset}: ConfigFormProps) => {
    const {register, handleSubmit, reset, formState: {errors}} = useForm<CropData>()

    const handleReset = () => {
        reset()
        onReset()
    }

    return (
        <form className="grid grid-cols-6 gap-x-2 gap-y-4" onSubmit={handleSubmit(onSubmit)} onReset={handleReset}>
            <label className="form-control col-span-3">
                <div className="label">
                    <span className="label-text">Mask</span>
                </div>
                <select className="select select-bordered" {...register("mask")} defaultValue={MaskEnum.BOX}>
                    <option value={MaskEnum.BOX}>Box</option>
                    <option value={MaskEnum.CIRCLE}>Circle</option>
                    <option value={MaskEnum.NONE}>None</option>
                </select>
            </label>
            <label className="form-control col-span-3">
                <div className="label">
                    <span className="label-text">Aspect Ratio</span>
                </div>
                <select className="select select-bordered" {...register("aspectRatio")} defaultValue={AspectRatioEnum.SQUARE}>
                    <option value={AspectRatioEnum.SQUARE}>Square (1:1)</option>
                    <option value={AspectRatioEnum.PORTRAIT}>Portrait (3:4)</option>
                    <option value={AspectRatioEnum.FREE}>Free (Use width and height)</option>
                </select>
            </label>
            {/* TODO: number inputs should be only enabled for certain values of the dropdowns*/}
            <label className="form-control col-span-2">
                <div className="label">
                    <span className="label-text">Height</span>
                </div>
                <input className={clsx("input input-bordered", errors.height && "input-error")}
                          {...register("height", {required: true, valueAsNumber: true})}
                       type="number" placeholder="Height" defaultValue="1000" />
                <div className="label">
                    <span className="label-text-alt text-error">
                        {errors.height?.type === "required" && "Required."}
                    </span>
                </div>
            </label>
            <label className="form-control col-span-2">
                <div className="label">
                    <span className="label-text">Width</span>
                </div>
                <input className={clsx("input input-bordered", errors.width && "input-error")}
                       {...register("width", {required: true, pattern: /^(\d+|auto)$/, setValueAs: (v) => (v === "auto" ? v : parseInt(v))})}
                       placeholder="Width" defaultValue="auto"/>
                <div className="label">
                    <span className="label-text-alt text-error">
                        {errors.width?.type === "required" && "Required."}
                        {errors.width?.type === "pattern" && "Must be a number or 'auto'."}
                    </span>
                </div>
            </label>
            <label className="form-control col-span-2">
                <div className="label">
                    <span className="label-text">Radius</span>
                </div>
                <input className={clsx("input input-bordered", errors.radius && "input-error")}
                       {...register("radius", {required: true, valueAsNumber: true})}
                       placeholder="Radius" type="number" defaultValue="100"/>
                <div className="label">
                    <span className="label-text-alt text-error">
                        {errors.radius?.type === "required" && "Required."}
                    </span>
                </div>
            </label>
            <button className="grow btn btn-primary col-span-3">Upload</button>
            <button className="grow btn col-span-3" type="reset">Reset</button>
        </form>
    )
}

export default ConfigForm
