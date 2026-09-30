import {
    deleteOutboxItem,
    getAllOutboxItems,
    updateOutboxItem,
} from "./db.js"

let synchronizationRunning = false

function createFormData(record) {
    const formData = new FormData()

    formData.append("client_uuid", record.client_uuid)

    for (const [field, value] of Object.entries(record.payload ?? {})) {
        if (value !== null && value !== undefined) {
            formData.append(field, String(value))
        }
    }

    for (const [field, file] of Object.entries(record.files ?? {})) {
        if (file instanceof Blob) {
            const filename =
                file.name || `${field}-${record.client_uuid}.jpg`

            formData.append(field, file, filename)
        }
    }

    return formData
}

async function readResponse(response) {
    try {
        return await response.json()
    } catch {
        return null
    }
}

function responseMessage(data, defaultMessage) {
    return (
        data?.error?.message ??
        data?.message ??
        defaultMessage
    )
}

export async function syncOutbox() {
    if (synchronizationRunning) {
        return {
            ok: false,
            code: "SYNC_ALREADY_RUNNING",
            message: "Ya existe una sincronización en curso",
        }
    }

    synchronizationRunning = true

    const summary = {
        synchronized: 0,
        pending: 0,
        requires_review: 0,
        requires_authentication: false,
    }

    try {
        const records = await getAllOutboxItems()

        const pendingRecords = records.filter(
            record =>
                record.status === "pending" ||
                record.status === "retry"
        )

        for (const record of pendingRecords) {
            let response

            try {
                response = await fetch(record.endpoint, {
                    method: "POST",
                    body: createFormData(record),
                    credentials: "same-origin",
                    headers: {
                        Accept: "application/json",
                    },
                })
            } catch (error) {
                await updateOutboxItem(record.client_uuid, {
                    status: "retry",
                    attempts: (record.attempts ?? 0) + 1,
                    last_error: error.message,
                    last_attempt_at: new Date().toISOString(),
                })

                summary.pending += 1
                continue
            }

            const data = await readResponse(response)

            if (response.ok) {
                await deleteOutboxItem(record.client_uuid)
                summary.synchronized += 1
                continue
            }

            if (response.status === 401) {
                await updateOutboxItem(record.client_uuid, {
                    status: "pending",
                    last_error: "Se requiere iniciar sesión",
                    last_attempt_at: new Date().toISOString(),
                })

                summary.requires_authentication = true
                break
            }

            if (response.status >= 400 && response.status < 500) {
                await updateOutboxItem(record.client_uuid, {
                    status: "requires_review",
                    attempts: (record.attempts ?? 0) + 1,
                    last_error: responseMessage(
                        data,
                        `Error HTTP ${response.status}`
                    ),
                    last_attempt_at: new Date().toISOString(),
                })

                summary.requires_review += 1
                continue
            }

            await updateOutboxItem(record.client_uuid, {
                status: "retry",
                attempts: (record.attempts ?? 0) + 1,
                last_error: responseMessage(
                    data,
                    `Error HTTP ${response.status}`
                ),
                last_attempt_at: new Date().toISOString(),
            })

            summary.pending += 1
        }

        return {
            ok: !summary.requires_authentication,
            ...summary,
        }
    } finally {
        synchronizationRunning = false
    }
}