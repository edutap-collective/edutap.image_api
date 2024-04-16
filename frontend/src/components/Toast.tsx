interface Toast {
    title: string,
    message: string
}

const Toast = ({title, message}: Toast) =>
    (
        <>
            <strong>{title}</strong>
            <p>{message}</p>
        </>
    )

export default Toast